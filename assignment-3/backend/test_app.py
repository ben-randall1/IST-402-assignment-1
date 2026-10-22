"""Fictional fixtures only. No model quota or hotel records are used."""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import httpx
from fastapi.testclient import TestClient

import main
import storage
from fixture_server import FixtureModel
from provider import ModelError, OpenRouter, validate


class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(storage, 'DATABASE_PATH', Path(self.temp.name) / 'test.db')
        self.db_patch.start()
        self.model_patch = patch.object(main, 'model', FixtureModel())
        self.model_patch.start()
        self.context = TestClient(main.app)
        self.client = self.context.__enter__()
        self.sid = str(uuid4())
        self.client.post('/api/sessions', json={'session_id': self.sid}).raise_for_status()

    def tearDown(self):
        self.context.__exit__(None, None, None)
        self.model_patch.stop(); self.db_patch.stop(); self.temp.cleanup()

    def read(self):
        return self.client.get(f'/api/sessions/{self.sid}').json()

    def send(self, text, request_id=None, revision=None):
        return self.client.post(f'/api/sessions/{self.sid}/messages', json={'request_id': request_id or str(uuid4()), 'expected_revision': self.read()['session']['revision'] if revision is None else revision, 'text': text})

    def update(self, status, active=0, paused=0, revision=None):
        return self.client.patch(f'/api/sessions/{self.sid}', json={'expected_revision': self.read()['session']['revision'] if revision is None else revision, 'status': status, 'active_ms': active, 'paused_ms': paused, 'replay_ms': 0, 'progress': {}})

    def test_conversation_idempotency_and_restart_persistence(self):
        rid = str(uuid4())
        first = self.send('Fictional: what do the counts mean?', rid)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()['response_id'], 'explain_breathing')
        self.assertIn('[MOCK RESPONSE]', first.json()['messages'][1]['content'])
        self.assertEqual(self.send('Same request', rid).status_code, 200)
        self.assertEqual(len(self.read()['messages']), 2)
        storage.initialize()
        self.assertEqual(len(self.read()['messages']), 2)
        self.assertIsNone(self.read()['messages'][1]['model_id'])

    def test_revision_and_time_constraints(self):
        self.assertEqual(self.update('completed', 60000).status_code, 409)
        self.assertEqual(self.update('active').status_code, 200)
        self.assertEqual(self.update('paused', 5000).status_code, 200)
        self.assertEqual(self.update('active', 4000).status_code, 422)
        self.assertEqual(self.update('active', 5000, revision=0).status_code, 409)
        self.assertEqual(self.update('active', 5000).status_code, 200)
        self.assertEqual(self.update('completed', 59000).status_code, 422)
        self.assertEqual(self.update('completed', 60013).status_code, 200)
        self.assertEqual(self.update('active', 60013).status_code, 409)

    def test_failed_attempt_is_persisted_without_success_or_automatic_retry(self):
        for marker, status in [('timeout', 504), ('rate limit', 429), ('malformed', 502), ('network', 502)]:
            rid = str(uuid4())
            response = self.send('Fictional: mock ' + marker, rid)
            self.assertEqual(response.status_code, status)
            self.assertEqual(self.send('Retry same UUID', rid).status_code, 409)
        record = self.read()
        self.assertEqual(len(record['messages']), 4)
        self.assertTrue(all(a['status'] == 'failed' for a in record['attempts']))
        self.assertEqual(self.update('active').status_code, 200)

    def test_crisis_rule_never_requires_a_model(self):
        with patch.object(main.model, 'select', side_effect=AssertionError('Must not call model')):
            response = self.send('Fictional scenario: I might hurt myself')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['crisis'])
        self.assertEqual(response.json()['messages'][1]['source'], 'fallback')
        self.assertIsNone(response.json()['proposal']['suggested_skill_id'])

    def test_usual_is_explicit_and_deletion_cascades(self):
        self.assertIsNone(self.client.get('/api/preferences/usual').json()['usual'])
        self.send('Fictional: choose something')
        self.assertIsNone(self.client.get('/api/preferences/usual').json()['usual'])
        self.client.put('/api/preferences/usual', json={'source_session_id': self.sid}).raise_for_status()
        self.assertEqual(self.send('Fictional: my usual?').json()['response_id'], 'usual_available')
        self.client.delete(f'/api/sessions/{self.sid}').raise_for_status()
        self.assertIsNone(self.client.get('/api/preferences/usual').json()['usual'])
        with storage.connection() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM messages').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM message_attempts').fetchone()[0], 0)
            tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertEqual(tables, {'skills', 'sessions', 'messages', 'preferences', 'message_attempts'})

    def test_context_is_current_session_bounded_and_preference_only_explicit(self):
        contexts = []
        def select(context):
            contexts.append(context)
            return {'response_id': 'offer_choice', 'suggested_skill_id': 'breathing-4-6'}, 'MOCK'
        other = str(uuid4())
        self.client.post('/api/sessions', json={'session_id': other})
        with patch.object(main.model, 'select', side_effect=select):
            for i in range(4): self.send(f'Fictional turn {i}')
        self.assertEqual(len(contexts[-1]['history']), 4)
        self.assertIsNone(contexts[-1]['explicit_preference'])
        self.assertFalse(any('session_id' in m for m in contexts[-1]['history']))
        self.assertEqual(self.client.get(f'/api/sessions/{other}').json()['messages'], [])

    def test_late_reply_cannot_replace_active_state(self):
        entered, release = threading.Event(), threading.Event()
        def slow(context):
            entered.set(); self.assertTrue(release.wait(5))
            return {'response_id': 'explain_breathing', 'suggested_skill_id': 'breathing-4-6'}, 'MOCK'
        responses = []
        with patch.object(main.model, 'select', side_effect=slow):
            worker = threading.Thread(target=lambda: responses.append(self.send('Fictional: counts?')))
            worker.start(); self.assertTrue(entered.wait(5))
            self.update('active').raise_for_status(); release.set(); worker.join(5)
        self.assertEqual(responses[0].status_code, 409)
        self.assertEqual(self.read()['attempts'][0]['status'], 'stale')
        self.assertEqual(len(self.read()['messages']), 1)

    def test_restart_marks_active_interrupted(self):
        self.update('active', 2000).raise_for_status()
        storage.initialize()
        self.assertEqual(self.read()['session']['status'], 'interrupted')
        self.assertEqual(self.read()['session']['active_ms'], 2000)

    def test_storage_failure_and_input_validation(self):
        with patch.object(storage, 'get_session', side_effect=__import__('sqlite3').OperationalError('secret internal detail')):
            result = self.client.get(f'/api/sessions/{self.sid}')
        self.assertEqual(result.status_code, 503)
        self.assertNotIn('secret internal', result.text)
        self.assertEqual(self.send(' ').status_code, 422)
        self.assertEqual(self.send('x'*501).status_code, 422)
        self.assertEqual(self.client.get('/api/sessions?limit=100').status_code, 422)


class AdapterTests(unittest.TestCase):
    def test_paid_fallback_missing_and_budget(self):
        with patch('provider.configuration', side_effect=ModelError('Missing', 503)):
            self.assertFalse(OpenRouter().configured)
        from provider import configuration
        with patch('provider.dotenv_values', return_value={'OPENROUTER_API_KEY': 'test-key', 'OPENROUTER_MODEL': 'nvidia/nemotron:paid'}), patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ModelError): configuration()
        with patch('provider.dotenv_values', return_value={'OPENROUTER_API_KEY': 'paste_your_key_here', 'OPENROUTER_MODEL': 'nvidia/nemotron:free'}), patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ModelError): configuration()
        model = OpenRouter(); model.calls = 50
        with patch('provider.configuration', return_value=('test-key', 'nvidia/nemotron:free')):
            with self.assertRaises(ModelError) as caught: model.select({})
        self.assertEqual(caught.exception.status, 429)

    def test_transport_statuses_and_invalid_payloads_are_safe(self):
        cases = [(429, {}, 429), (401, {'error':'test-key'}, 503), (200, {'choices':[]}, 502), (200, {'choices':[{'finish_reason':'length','message':{'content':'{}'}}]},502), (200, {'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'response_id':'invented','suggested_skill_id':None})}}]},502)]
        for status, body, expected in cases:
            with self.subTest(status=status, body=body), patch('provider.configuration', return_value=('test-key','nvidia/nemotron:free')), patch('httpx.Client.post', return_value=httpx.Response(status, json=body)):
                with self.assertRaises(ModelError) as caught: OpenRouter().select({})
                self.assertEqual(caught.exception.status, expected)
                self.assertNotIn('test-key', str(caught.exception))
        for error, expected in [(httpx.ReadTimeout('test-key'),504), (httpx.ConnectError('test-key'),502)]:
            with patch('provider.configuration', return_value=('test-key','nvidia/nemotron:free')), patch('httpx.Client.post', side_effect=error):
                with self.assertRaises(ModelError) as caught: OpenRouter().select({})
                self.assertEqual(caught.exception.status,expected)
                self.assertNotIn('test-key',str(caught.exception))

    def test_valid_live_transport_selects_only_reviewed_id(self):
        proposal = {'response_id':'explain_breathing','suggested_skill_id':'breathing-4-6'}
        body = {'choices':[{'finish_reason':'stop','message':{'content':json.dumps(proposal)}}]}
        with patch('provider.configuration',return_value=('test-key','nvidia/nemotron:free')),patch('httpx.Client.post',return_value=httpx.Response(200,json=body)) as post:
            result, model = OpenRouter().select({'question':'Fictional counts?'})
        self.assertEqual(result,proposal)
        self.assertEqual(model,'nvidia/nemotron:free')
        self.assertEqual(post.call_args.kwargs['json']['messages'][0]['role'],'system')
        self.assertFalse(post.call_args.kwargs['json']['reasoning']['enabled'])
        self.assertEqual(post.call_args.kwargs['json']['max_tokens'],512)

    def test_validation_rejects_invention_and_inferred_preference(self):
        invalid = [{}, {'response_id':'usual_available','suggested_skill_id':'breathing-4-6'}, {'response_id':'outside_scope','suggested_skill_id':'breathing-4-6'}, {'response_id':'offer_choice','suggested_skill_id':'new-skill'}, {'response_id':'offer_choice','suggested_skill_id':None,'advice':'unreviewed'}]
        for item in invalid:
            with self.assertRaises(ValueError): validate(item,{})

if __name__ == '__main__': unittest.main()
