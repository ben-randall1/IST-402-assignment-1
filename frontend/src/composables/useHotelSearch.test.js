import { test } from 'node:test'
import assert from 'node:assert/strict'
import { useHotelSearch } from './useHotelSearch.js'

const apiFixture = {
  center: { postcode: '02108', country_code: 'us', locality: 'Boston', latitude: 42.357, longitude: -71.063 },
  hotels: [{ place_id: 'fixture-1', provider: 'geoapify', name: 'Fixture Hotel', address: null, latitude: 42.358, longitude: -71.064, distance_meters: 100 }],
}
const localEmpty = { source: 'local', zip_code: '02108', count: 0, hotels: [] }
const localFixture = {
  source: 'local', count: 1, center: apiFixture.center,
  hotels: [{ ...apiFixture.hotels[0], saved_locally: true, demo_nights: [{ stay_date: '2026-10-10', nightly_rate_cents: 10000, rooms_available: 20 }] }],
}
const reply = (status, data) => ({ ok: status < 400, status, json: async () => data })

test('invalid ZIP never reaches local storage or the provider', async () => {
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

test('an empty local lookup falls back to the existing API with a leading-zero ZIP', async () => {
  const requests = []
  globalThis.fetch = async url => {
    requests.push(url)
    return url.startsWith('/api/local-hotels') ? reply(200, localEmpty) : reply(200, apiFixture)
  }
  const search = useHotelSearch()
  await search.search(' 02108 ')
  assert.deepEqual(requests, ['/api/local-hotels?zip_code=02108', '/api/hotels?zip_code=02108'])
  assert.equal(search.zipCode.value, '02108')
  assert.equal(search.result.value.source, 'api')
  assert.equal(search.hotels.value[0].saved_locally, false)
})

test('a nonempty local lookup never calls the Part 1 hotel endpoint', async () => {
  const requests = []
  globalThis.fetch = async url => { requests.push(url); return reply(200, localFixture) }
  const search = useHotelSearch()
  await search.search('02108')
  assert.deepEqual(requests, ['/api/local-hotels?zip_code=02108'])
  assert.equal(search.state.value, 'results')
  assert.equal(search.result.value.source, 'local')
})

test('a successful API empty result retains its verified center', async () => {
  globalThis.fetch = async url => url.startsWith('/api/local-hotels') ? reply(200, localEmpty) : reply(200, { ...apiFixture, hotels: [] })
  const search = useHotelSearch()
  await search.search('02108')
  assert.equal(search.state.value, 'empty')
  assert.equal(search.result.value.center.postcode, '02108')
})

test('a failed local read stops before the API and remains an error', async () => {
  const requests = []
  globalThis.fetch = async url => { requests.push(url); return reply(500, { detail: 'Local hotel storage could not be read.' }) }
  const search = useHotelSearch()
  await search.search('02108')
  assert.deepEqual(requests, ['/api/local-hotels?zip_code=02108'])
  assert.equal(search.state.value, 'error')
  assert.equal(search.result.value, null)
  assert.match(search.errorMessage.value, /Local hotel storage/)
})

test('API unresolved, quota, and provider errors have distinct safe UI outcomes', async () => {
  for (const [status, state] of [[404, 'unresolved'], [422, 'invalid'], [429, 'error'], [502, 'error'], [503, 'error']]) {
    globalThis.fetch = async url => url.startsWith('/api/local-hotels') ? reply(200, localEmpty) : reply(status, { detail: 'Safe service explanation' })
    const search = useHotelSearch()
    await search.search('02108')
    assert.equal(search.state.value, state)
    assert.equal(search.errorMessage.value, 'Safe service explanation')
  }
})

test('saving marks a live API result only after backend success', async () => {
  const search = useHotelSearch()
  globalThis.fetch = async url => url.startsWith('/api/local-hotels') ? reply(200, localEmpty) : reply(200, apiFixture)
  await search.search('02108')
  const hotel = search.hotels.value[0]
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/local-hotels')
    assert.equal(options.method, 'POST')
    return reply(201, { message: 'Hotel saved locally with five simulated nightly records.' })
  }
  await search.saveHotel(hotel)
  assert.equal(hotel.saved_locally, true)
  assert.match(search.actionMessage.value, /saved locally/)
})

test('removing a saved local hotel updates only after backend success', async () => {
  const search = useHotelSearch()
  globalThis.fetch = async () => reply(200, localFixture)
  await search.search('02108')
  search.selectedId.value = 'fixture-1'
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/local-hotels/fixture-1')
    assert.equal(options.method, 'DELETE')
    return reply(200, { message: 'Hotel and its local classroom records were removed.' })
  }
  await search.removeHotel(search.hotels.value[0])
  assert.equal(search.hotels.value.length, 0)
  assert.equal(search.selectedId.value, null)
  assert.equal(search.state.value, 'empty')
})

test('a stale local response cannot replace a newer search', async () => {
  let finishOld
  globalThis.fetch = () => new Promise(resolve => { finishOld = resolve })
  const search = useHotelSearch()
  const oldRequest = search.search('16802')
  assert.equal(search.state.value, 'loading')
  globalThis.fetch = async url => url.startsWith('/api/local-hotels') ? reply(200, localFixture) : reply(200, apiFixture)
  await search.search('02108')
  finishOld(reply(200, { ...localFixture, center: { ...apiFixture.center, postcode: '16802' } }))
  await oldRequest
  assert.equal(search.result.value.center.postcode, '02108')
})
