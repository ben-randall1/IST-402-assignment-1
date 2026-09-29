import { test } from 'node:test'
import assert from 'node:assert/strict'
import { useHotelSearch } from './useHotelSearch.js'

const fixture = { center: { postcode: '02108', locality: 'Boston', latitude: 42.357, longitude: -71.063 }, hotels: [{ place_id: 'fixture-1', name: null }] }
const reply = (status, data) => ({ ok: status < 400, status, json: async () => data })

test('invalid ZIP never reaches the provider and clears an old selection', async () => {
  const search = useHotelSearch()
  search.selectedId.value = 'old'
  globalThis.fetch = () => { throw new Error('fetch must not run') }
  for (const zip of ['1234', '123456', '１２３４５', 'abcde', '']) {
    await search.search(zip)
    assert.equal(search.state.value, 'invalid')
    assert.equal(search.result.value, null)
    assert.equal(search.selectedId.value, null)
  }
})

test('a successful leading-zero search retains the ZIP and shared selected hotel', async () => {
  const search = useHotelSearch()
  globalThis.fetch = async url => { assert.ok(url.endsWith('zip_code=02108')); return reply(200, fixture) }
  await search.search(' 02108 ')
  assert.equal(search.zipCode.value, '02108')
  assert.equal(search.state.value, 'results')
  search.selectedId.value = 'fixture-1'
  assert.equal(search.selectedHotel.value.place_id, 'fixture-1')
})

test('successful empty result retains its verified center', async () => {
  globalThis.fetch = async () => reply(200, { ...fixture, hotels: [] })
  const search = useHotelSearch()
  await search.search('02108')
  assert.equal(search.state.value, 'empty')
  assert.equal(search.result.value.center.postcode, '02108')
})

test('unresolved ZIP, invalid input, rate limit and provider failures have distinct states', async () => {
  for (const [status, state] of [[404, 'unresolved'], [422, 'invalid'], [429, 'error'], [502, 'error'], [503, 'error']]) {
    globalThis.fetch = async () => reply(status, { detail: 'Safe service explanation' })
    const search = useHotelSearch()
    await search.search('02108')
    assert.equal(search.state.value, state)
    assert.equal(search.errorMessage.value, 'Safe service explanation')
    assert.equal(search.result.value, null)
  }
})

test('network and malformed response failures cannot look like empty results', async () => {
  for (const stub of [async () => { throw new TypeError('offline') }, async () => reply(200, {})]) {
    globalThis.fetch = stub
    const search = useHotelSearch()
    await search.search('02108')
    assert.equal(search.state.value, 'error')
    assert.equal(search.result.value, null)
  }
})

test('loading appears before response and a stale request cannot replace the newer search', async () => {
  let finishOld
  let oldSignal
  globalThis.fetch = (_url, options) => { oldSignal = options.signal; return new Promise(resolve => { finishOld = resolve }) }
  const search = useHotelSearch()
  const oldRequest = search.search('16802')
  assert.equal(search.state.value, 'loading')
  globalThis.fetch = async () => reply(200, fixture)
  await search.search('02108')
  assert.ok(oldSignal.aborted)
  finishOld(reply(200, { ...fixture, center: { postcode: '16802' } }))
  await oldRequest
  assert.equal(search.result.value.center.postcode, '02108')
})

test('cancelled component cannot be updated by a late request', async () => {
  let finish
  globalThis.fetch = () => new Promise(resolve => { finish = resolve })
  const search = useHotelSearch()
  const pending = search.search('02108')
  search.cancel()
  finish(reply(200, fixture))
  await pending
  assert.equal(search.result.value, null)
})
