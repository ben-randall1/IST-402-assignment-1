import { computed, ref } from 'vue'

export function useHotelSearch() {
  const zipCode = ref('16802')
  const state = ref('idle')
  const result = ref(null)
  const errorMessage = ref('')
  const actionMessage = ref('')
  const selectedId = ref(null)
  const pendingHotelIds = ref(new Set())
  const hotels = computed(() => result.value?.hotels || [])
  const selectedHotel = computed(() => hotels.value.find(h => h.place_id === selectedId.value))
  let requestNumber = 0
  let controller

  function setPending(placeId, pending) {
    const next = new Set(pendingHotelIds.value)
    pending ? next.add(placeId) : next.delete(placeId)
    pendingHotelIds.value = next
  }

  async function readJson(path, options = {}) {
    const response = await fetch(path, options)
    const payload = await response.json().catch(() => ({}))
    if (!response.ok) {
      const error = new Error(typeof payload.detail === 'string' ? payload.detail : 'The local hotel service could not complete that request.')
      error.status = response.status
      throw error
    }
    return payload
  }

  async function search(zip = zipCode.value) {
    const request = ++requestNumber
    controller?.abort()
    result.value = null
    selectedId.value = null
    errorMessage.value = ''
    actionMessage.value = ''
    zipCode.value = zip.trim()
    if (!/^[0-9]{5}$/.test(zipCode.value)) {
      state.value = 'invalid'
      errorMessage.value = 'Enter exactly five digits, including any leading zero.'
      return
    }
    state.value = 'loading'
    controller = new AbortController()
    const currentController = controller
    const timeout = setTimeout(() => currentController.abort(), 25000)
    let requestSource = 'local'
    try {
      const local = await readJson(`/api/local-hotels?zip_code=${encodeURIComponent(zipCode.value)}`, { signal: currentController.signal })
      if (request !== requestNumber) return
      if (local.count > 0) {
        result.value = { ...local, source: 'local', hotels: local.hotels.map(hotel => ({ ...hotel, saved_locally: true })) }
        state.value = 'results'
        actionMessage.value = `Showing ${local.count} saved local hotel${local.count === 1 ? '' : 's'} for ZIP ${zipCode.value}.`
        return
      }
      requestSource = 'api'
      const api = await readJson(`/api/hotels?zip_code=${encodeURIComponent(zipCode.value)}`, { signal: currentController.signal })
      if (request !== requestNumber) return
      if (!api.center || !Array.isArray(api.hotels)) throw new Error('Unexpected response')
      result.value = { ...api, source: 'api', hotels: api.hotels.map(hotel => ({ ...hotel, saved_locally: false })) }
      state.value = api.hotels.length ? 'results' : 'empty'
    } catch (error) {
      if (request !== requestNumber) return
      if (error.name === 'AbortError') {
        state.value = 'error'
        errorMessage.value = 'The search took too long. Please try again.'
      } else {
        state.value = requestSource === 'api' && error.status === 404
          ? 'unresolved'
          : requestSource === 'api' && error.status === 422
            ? 'invalid'
            : 'error'
        errorMessage.value = error.message || 'We couldn’t reach the hotel search service. Check your connection and try again.'
      }
    } finally {
      clearTimeout(timeout)
    }
  }

  async function saveHotel(hotel) {
    if (!result.value || pendingHotelIds.value.has(hotel.place_id)) return
    setPending(hotel.place_id, true)
    actionMessage.value = ''
    try {
      const saved = await readJson('/api/local-hotels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hotel, zip_code: zipCode.value, center: result.value.center }),
      })
      hotel.saved_locally = true
      actionMessage.value = saved.message
    } catch (error) {
      actionMessage.value = error.message || 'This hotel could not be saved locally. Please try again.'
    } finally {
      setPending(hotel.place_id, false)
    }
  }

  async function removeHotel(hotel) {
    if (!result.value || pendingHotelIds.value.has(hotel.place_id)) return
    setPending(hotel.place_id, true)
    actionMessage.value = ''
    try {
      const removed = await readJson(`/api/local-hotels/${encodeURIComponent(hotel.place_id)}`, { method: 'DELETE' })
      result.value.hotels = result.value.hotels.filter(candidate => candidate.place_id !== hotel.place_id)
      if (selectedId.value === hotel.place_id) selectedId.value = null
      state.value = result.value.hotels.length ? 'results' : 'empty'
      actionMessage.value = removed.message
    } catch (error) {
      actionMessage.value = error.message || 'This saved hotel could not be removed. Please try again.'
    } finally {
      setPending(hotel.place_id, false)
    }
  }

  function cancel() { requestNumber++; controller?.abort() }
  return { zipCode, state, result, errorMessage, actionMessage, selectedId, selectedHotel, hotels, pendingHotelIds, search, saveHotel, removeHotel, cancel }
}
