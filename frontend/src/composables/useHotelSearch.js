import { computed, ref } from 'vue'

export function useHotelSearch() {
  const zipCode = ref('16802')
  const state = ref('idle')
  const result = ref(null)
  const errorMessage = ref('')
  const selectedId = ref(null)
  const hotels = computed(() => result.value?.hotels || [])
  const selectedHotel = computed(() => hotels.value.find(h => h.place_id === selectedId.value))
  let requestNumber = 0
  let controller

  async function search(zip = zipCode.value) {
    const request = ++requestNumber
    controller?.abort()
    result.value = null
    selectedId.value = null
    errorMessage.value = ''
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
    try {
      const response = await fetch(`/api/hotels?zip_code=${encodeURIComponent(zipCode.value)}`, { signal: currentController.signal })
      const payload = await response.json()
      if (request !== requestNumber) return
      if (!response.ok) {
        state.value = response.status === 404 ? 'unresolved' : response.status === 422 ? 'invalid' : 'error'
        errorMessage.value = typeof payload.detail === 'string' ? payload.detail : 'The search service could not complete your request. Please try again.'
        return
      }
      if (!payload.center || !Array.isArray(payload.hotels)) throw new Error('Unexpected response')
      result.value = payload
      state.value = payload.hotels.length ? 'results' : 'empty'
    } catch (error) {
      if (request !== requestNumber) return
      state.value = 'error'
      errorMessage.value = error.name === 'AbortError'
        ? 'The search took too long. Please try again.'
        : 'We couldn’t reach the hotel search service. Check your connection and try again.'
    } finally {
      clearTimeout(timeout)
    }
  }
  function cancel() { requestNumber++; controller?.abort() }
  return { zipCode, state, result, errorMessage, selectedId, selectedHotel, hotels, search, cancel }
}
