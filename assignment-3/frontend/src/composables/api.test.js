import test from 'node:test'
import assert from 'node:assert/strict'
import { request } from './api.js'
const originalFetch = globalThis.fetch
test.afterEach(() => { globalThis.fetch = originalFetch })
test('quota failure remains an error with its status, not empty successful data', async () => {
  globalThis.fetch = async () => ({ ok:false, status:429, json:async()=>({detail:'Usage limit reached'}) })
  await assert.rejects(request('/api/example'), error => error.status === 429 && error.message === 'Usage limit reached')
})
test('invalid JSON and network failure never become a successful empty result', async () => {
  globalThis.fetch = async () => ({ ok:true, json:async()=>{throw new SyntaxError('bad payload')} })
  await assert.rejects(request('/api/example'), /unreadable response/)
  globalThis.fetch = async () => { throw new TypeError('Network unavailable') }
  await assert.rejects(request('/api/example'), /Network unavailable/)
})
test('explicit cancellation reaches the request rather than retrying it', async () => {
  const controller=new AbortController();controller.abort();let count=0
  globalThis.fetch = async (_, options) => { count++;options.signal.throwIfAborted() }
  await assert.rejects(request('/api/example',{signal:controller.signal}), error => error.name==='AbortError')
  assert.equal(count,1)
})
