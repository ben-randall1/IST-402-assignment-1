"""Explicit MOCK server with disposable SQLite. Never imported by the normal app."""
import tempfile
from pathlib import Path

import main
import storage
from provider import ModelError, validate


class FixtureModel:
    mode = 'fixture'
    configured = True
    calls = 0  # No live provider calls.

    def select(self, context):
        text = context['question'].casefold()
        for marker, status in [('mock timeout', 504), ('mock rate limit', 429), ('mock malformed', 502), ('mock network', 502)]:
            if marker in text:
                raise ModelError(f'[MOCK FAILURE] {marker}. Continue without a reply.', status)
        if 'usual' in text and context.get('explicit_preference'):
            code = 'usual_available'
        elif any(term in text for term in ('diagnose', 'medication', 'ignore the rules')):
            code = 'outside_scope'
        elif any(term in text for term in ('count', 'explain', 'mean')):
            code = 'explain_breathing'
        elif any(term in text for term in ('leave', 'different')):
            code = 'different_choice'
        else:
            code = 'offer_choice'
        return validate({'response_id': code, 'suggested_skill_id': None if code == 'outside_scope' else 'breathing-4-6'}, context), 'MOCK:reviewed-response-fixture'


if __name__ == '__main__':
    import uvicorn
    with tempfile.TemporaryDirectory(prefix='little-space-MOCK-') as directory:
        storage.DATABASE_PATH = Path(directory) / 'fixture.db'
        main.model = FixtureModel()
        print('MOCK MODEL MODE — temporary SQLite; no external model calls. Database:', storage.DATABASE_PATH)
        uvicorn.run(main.app, host='127.0.0.1', port=8001, access_log=False)
