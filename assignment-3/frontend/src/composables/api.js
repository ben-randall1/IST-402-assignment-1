export async function request(path, options = {}) {
  const { signal, ...rest } = options
  const timeout = AbortSignal.timeout(15000)
  const response = await fetch(path, { ...rest, signal: signal ? AbortSignal.any([signal, timeout]) : timeout, headers: { 'Content-Type': 'application/json', ...rest.headers } })
  let payload
  try { payload = await response.json() } catch { throw new Error('The local service returned an unreadable response. The practice and support information are still available.') }
  if (!response.ok) {
    const error = new Error(typeof payload.detail === 'string' ? payload.detail : 'The local service could not finish that request.')
    error.status = response.status
    throw error
  }
  return payload
}
