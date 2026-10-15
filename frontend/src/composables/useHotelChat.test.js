import test, { afterEach } from 'node:test'
import assert from 'node:assert/strict'
import { useHotelChat } from './useHotelChat.js'

const originalFetch = globalThis.fetch
afterEach(() => { globalThis.fetch = originalFetch })
const success = { status: 'answer', answer: 'Pine costs $200 [1]. Simulated data.', records: [{ hotel_id: 'fixture-pine' }], proposed_sql: 'SELECT hotel_id FROM saved_hotels', citations: [1] }
const reply = (status, payload) => ({ ok: status < 400, json: async () => payload })

test('blank or excessive questions do not call the backend', async () => {
  globalThis.fetch = () => { throw new Error('Should not fetch') }
  const chat = useHotelChat()
  for (const question of [' ', 'a'.repeat(1201)]) {
    await chat.ask(question)
    assert.equal(chat.state.value, 'error')
  }
})
test('question POST transitions through loading to grounded answer', async () => {
  const chat = useHotelChat()
  globalThis.fetch = async (url, options) => {
    assert.equal(chat.state.value, 'loading')
    assert.equal(url, '/api/chat')
    assert.equal(options.method, 'POST')
    assert.deepEqual(JSON.parse(options.body), { question: 'Which hotels?' })
    return reply(200, success)
  }
  await chat.ask(' Which hotels? ')
  assert.equal(chat.state.value, 'answer')
  assert.equal(chat.result.value.answer, success.answer)
})
test('successful no-match differs from error and clears prior answer', async () => {
  const chat = useHotelChat()
  globalThis.fetch = async () => reply(200, success)
  await chat.ask('Hotels?')
  globalThis.fetch = async () => reply(200, { ...success, status: 'no_matches', records: [], citations: [], answer: 'No matching saved data.' })
  await chat.ask('Other dates?')
  assert.equal(chat.state.value, 'no_matches')
  assert.deepEqual(chat.result.value.records, [])
  globalThis.fetch = async () => reply(429, { detail: 'Usage limit reached.' })
  await chat.ask('Hotels?')
  assert.equal(chat.state.value, 'error')
  assert.equal(chat.result.value, null)
})
test('failures, malformed payloads, and network errors never become no matches', async () => {
  for (const response of [reply(503, { detail: 'Configure the backend key.' }), reply(422, { detail: 'Query rejected.' }), reply(200, {}), reply(200, { ...success, status: 'no_matches' })]) {
    globalThis.fetch = async () => response
    const chat = useHotelChat()
    await chat.ask('Hotels?')
    assert.equal(chat.state.value, 'error')
    assert.equal(chat.result.value, null)
  }
  globalThis.fetch = async () => { throw new TypeError('Network unavailable') }
  const chat = useHotelChat()
  await chat.ask('Hotels?')
  assert.equal(chat.state.value, 'error')
})
test('newer question wins and cancellation ignores late results', async () => {
  let finish
  globalThis.fetch = () => new Promise(resolve => { finish = resolve })
  const chat = useHotelChat()
  const first = chat.ask('First?')
  globalThis.fetch = async () => reply(200, { ...success, answer: 'New answer' })
  await chat.ask('Second?')
  finish(reply(200, success))
  await first
  assert.equal(chat.result.value.answer, 'New answer')
  globalThis.fetch = () => new Promise(resolve => { finish = resolve })
  const pending = chat.ask('Third?')
  chat.cancel()
  finish(reply(200, success))
  await pending
  assert.equal(chat.state.value, 'idle')
  assert.equal(chat.result.value, null)
})
