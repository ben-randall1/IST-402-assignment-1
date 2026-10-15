import { ref } from 'vue'

export function useHotelChat() {
  const question = ref('')
  const state = ref('idle')
  const errorMessage = ref('')
  const result = ref(null)
  let sequence = 0
  let controller

  async function ask(text = question.value) {
    const request = ++sequence
    controller?.abort()
    question.value = text.trim()
    result.value = null
    errorMessage.value = ''
    if (!question.value || question.value.length > 1200) {
      state.value = 'error'
      errorMessage.value = 'Enter a hotel question between 1 and 1,200 characters.'
      return
    }
    state.value = 'loading'
    controller = new AbortController()
    const activeController = controller
    const timeout = setTimeout(() => activeController.abort(), 120000)
    try {
      const response = await fetch('/api/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.value }), signal: activeController.signal,
      })
      const payload = await response.json()
      if (request !== sequence) return
      if (!response.ok) throw new Error(typeof payload.detail === 'string' ? payload.detail : 'The assistant could not complete your question.')
      if (!['answer', 'no_matches'].includes(payload.status) || typeof payload.answer !== 'string' || !payload.answer.trim() || !Array.isArray(payload.records) || typeof payload.proposed_sql !== 'string' || !Array.isArray(payload.citations) || (payload.status === 'answer') !== (payload.records.length > 0)) {
        throw new Error('The assistant returned an unexpected response. Please try again.')
      }
      result.value = payload
      state.value = payload.status
    } catch (error) {
      if (request !== sequence) return
      state.value = 'error'
      errorMessage.value = error.name === 'AbortError'
        ? 'The assistant took too long. Please try again.'
        : error instanceof SyntaxError ? 'The assistant returned an unreadable response. Please try again.'
          : error.message || 'Could not reach the assistant. Check your connection and retry.'
    } finally {
      clearTimeout(timeout)
    }
  }

  function cancel() {
    sequence++
    controller?.abort()
    if (state.value === 'loading') state.value = 'idle'
  }
  return { question, state, errorMessage, result, ask, cancel }
}
