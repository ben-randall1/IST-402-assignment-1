import { ref, computed, nextTick, onBeforeUnmount } from 'vue'
import { PracticeClock } from './practiceClock.js'
import { request } from './api.js'

export function usePractice() {
  const screen = ref('home'), snapshot = ref({ status: 'ready', phase: 'inhale', round: 1, count: 4, active_ms: 0, paused_ms: 0, replay_ms: 0, trace: [] })
  const session = ref(null), messages = ref([]), usual = ref(null), history = ref([]), detail = ref(null)
  const saveState = ref('idle'), storageError = ref(''), chatError = ref(''), loadingMessage = ref(false), question = ref('')
  const supportOpen = ref(false), simple = ref(false), reducedMotion = ref(matchMedia('(prefers-reduced-motion: reduce)').matches)
  const health = ref(null), measurement = ref(null)
  let entryAt = performance.now()
  let clock = null, ticker, queue = Promise.resolve(), generation = 0, chatGeneration = 0, chatController, firstCue = null, lastSavedPhase = null
  const active = computed(() => snapshot.value.status === 'active')
  function cancelMessage() { chatGeneration++; chatController?.abort(); loadingMessage.value = false }

  async function initialize() {
    // Capture only the previous page's record before asynchronous setup.
    // A new user choice must never be mistaken for an interrupted prior session.
    const old = sessionStorage.getItem('little-space-session')
    try { health.value = await request('/api/health') } catch { health.value = { mode: 'unavailable', model_configured: false } }
    try { usual.value = (await request('/api/preferences/usual')).usual } catch { storageError.value = 'Local history is unavailable. You can still choose the fixed practice.' }
    if (old) {
      try {
        const record = (await request(`/api/sessions/${old}`)).session
        if (['ready', 'active', 'paused'].includes(record.status)) {
          await request(`/api/sessions/${old}`, { method: 'PATCH', body: JSON.stringify({ expected_revision: record.revision, status: 'interrupted', active_ms: record.active_ms, paused_ms: record.paused_ms, replay_ms: record.replay_ms, progress: { ...record.progress, interruption: 'browser reload; last checkpoint only' } }) })
        }
      } catch { storageError.value = 'A prior session may have an incomplete checkpoint. Review local history; nothing was restarted.' }
      if (sessionStorage.getItem('little-space-session') === old) sessionStorage.removeItem('little-space-session')
    }
  }

  async function choose() {
    if (clock && ['ready', 'active', 'paused'].includes(snapshot.value.status)) { stop(); await queue }
    const run = ++generation
    entryAt = performance.now()
    cancelMessage(); clearInterval(ticker)
    clock = new PracticeClock()
    snapshot.value = clock.snapshot(); session.value = null; messages.value = []; detail.value = null; measurement.value = null; firstCue = null; lastSavedPhase = null
    storageError.value = ''; chatError.value = ''; question.value = ''; screen.value = 'ready'; saveState.value = 'saving'
    const id = crypto.randomUUID()
    queue = queue.catch(() => {}).then(async () => {
      try {
        const created = await request('/api/sessions', { method: 'POST', body: JSON.stringify({ session_id: id }) })
        if (run !== generation) return
        session.value = created
        sessionStorage.setItem('little-space-session', id)
        saveState.value = 'saved'
      } catch { if (run === generation) { saveState.value = 'error'; storageError.value = 'This session could not be created in local history. You can still use the practice and crisis information.' } }
    })
    await queue
  }

  function persist(value = snapshot.value) {
    const run = generation
    const captured = JSON.parse(JSON.stringify(value))
    const capturedMeasurement = measurement.value ? { ...measurement.value } : null
    saveState.value = 'saving'
    queue = queue.catch(() => {}).then(async () => {
      if (run !== generation) return
      if (!session.value) { saveState.value = 'error'; return }
      try {
        const current = (await request(`/api/sessions/${session.value.session_id}`)).session
        const saved = await request(`/api/sessions/${current.session_id}`, { method: 'PATCH', body: JSON.stringify({ expected_revision: current.revision, status: captured.status, active_ms: captured.active_ms, paused_ms: captured.paused_ms, replay_ms: captured.replay_ms, progress: { planned_ms: captured.planned_ms, phase: captured.phase, round: captured.round, trace: captured.trace.slice(-24), measurement: capturedMeasurement } }) })
        if (run !== generation) return
        session.value = saved; saveState.value = 'saved'; storageError.value = ''
        if (['completed', 'stopped', 'interrupted'].includes(saved.status)) sessionStorage.removeItem('little-space-session')
      } catch { if (run === generation) { saveState.value = 'error'; storageError.value = 'This checkpoint could not be saved. The exercise still works; history may be incomplete.' } }
    })
    return queue
  }

  function finish() {
    clearInterval(ticker)
    screen.value = 'ended'
    nextTick(() => {
      const ended = performance.now()
      measurement.value = { first_cue_at: firstCue, final_step_at: ended, setup_ms: Math.round((firstCue ?? ended) - entryAt), observed_sequence_ms: Math.round(ended - (firstCue ?? ended)), active_ms: snapshot.value.active_ms, paused_ms: snapshot.value.paused_ms, replay_ms: snapshot.value.replay_ms, planned_ms: 60000 }
      persist()
    })
  }
  function tick() {
    if (!clock) return
    snapshot.value = clock.snapshot()
    if (snapshot.value.status === 'completed') finish()
    else {
      const phaseKey = `${snapshot.value.round}:${snapshot.value.phase}`
      if (phaseKey !== lastSavedPhase) { lastSavedPhase = phaseKey; persist() }
    }
  }

  async function start() {
    if (!clock || snapshot.value.status !== 'ready') return
    cancelMessage(); clock.start(); snapshot.value = clock.snapshot(); screen.value = 'practice'
    await nextTick(); firstCue = performance.now()
    measurement.value = { first_cue_at: firstCue, setup_ms: Math.round(firstCue - entryAt) }
    persist(); ticker = setInterval(tick, 100)
  }
  function pause(reason = 'user') {
    if (!clock || !active.value) return
    clearInterval(ticker); snapshot.value = clock.pause(reason)
    if (snapshot.value.status === 'completed') finish()
    else { screen.value = 'paused'; persist() }
  }
  function resume() {
    if (!clock || snapshot.value.status !== 'paused') return
    snapshot.value = clock.resume(); screen.value = 'practice'; persist(); ticker = setInterval(tick, 100)
  }
  function stop() {
    cancelMessage(); clearInterval(ticker)
    question.value = ''
    if (clock && !['completed', 'stopped'].includes(snapshot.value.status)) { snapshot.value = clock.stop(); persist() }
    screen.value = 'stopped'
  }
  function openSupport() { pause('crisis information opened'); supportOpen.value = true }
  function openPrivacy() { pause('privacy information opened'); screen.value = 'privacy' }

  async function send() {
    const text = question.value.trim()
    if (!text || text.length > 500) { chatError.value = 'Use a fictional message of 1–500 characters, or skip to the practice.'; return }
    const run = generation, requestGeneration = ++chatGeneration
    chatController?.abort(); chatController = new AbortController(); loadingMessage.value = true; chatError.value = ''
    try {
      await queue
      if (run !== generation || requestGeneration !== chatGeneration) return
      if (!session.value) throw new Error('A saved session is needed for conversation. The fixed practice remains available.')
      const fresh = (await request(`/api/sessions/${session.value.session_id}`)).session
      const result = await request(`/api/sessions/${fresh.session_id}/messages`, { method: 'POST', signal: chatController.signal, body: JSON.stringify({ request_id: crypto.randomUUID(), expected_revision: fresh.revision, text }) })
      if (run !== generation || requestGeneration !== chatGeneration || snapshot.value.status !== 'ready') return
      session.value = result.session; messages.value = result.messages; question.value = ''
      if (result.crisis) openSupport()
    } catch (error) {
      if (run !== generation || requestGeneration !== chatGeneration) return
      chatError.value = error.name === 'AbortError' || error.name === 'TimeoutError' ? 'The message took too long. Continue without a reply or explicitly try again.' : error.message
      if (session.value) {
        try { const saved = await request(`/api/sessions/${session.value.session_id}`); if (run === generation && requestGeneration === chatGeneration) { session.value = saved.session; messages.value = saved.messages } } catch { /* The existing warning remains. */ }
      }
    } finally { if (requestGeneration === chatGeneration) loadingMessage.value = false }
  }

  async function loadHistory() {
    pause('history opened'); cancelMessage(); screen.value = 'history'; detail.value = null
    try { await queue; history.value = (await request('/api/sessions?limit=50')).sessions; storageError.value = '' } catch (error) { storageError.value = error.message }
  }
  async function inspect(id) {
    try { detail.value = await request(`/api/sessions/${id}`) } catch (error) { storageError.value = error.message }
  }
  async function remove(id) {
    if (!confirm('Delete this fictional session, its messages, and any usual choice based on it? This cannot be undone.')) return
    try {
      await request(`/api/sessions/${id}`, { method: 'DELETE' })
      if (session.value?.session_id === id) { cancelMessage(); session.value = null; sessionStorage.removeItem('little-space-session') }
      detail.value = null; usual.value = (await request('/api/preferences/usual')).usual; await loadHistory()
    } catch (error) { storageError.value = error.message }
  }
  async function remember(id = session.value?.session_id) {
    if (!id) return
    try { await queue; usual.value = (await request('/api/preferences/usual', { method: 'PUT', body: JSON.stringify({ source_session_id: id }) })).usual } catch (error) { storageError.value = error.message }
  }
  async function clearUsual() {
    try { usual.value = (await request('/api/preferences/usual', { method: 'DELETE' })).usual } catch (error) { storageError.value = error.message }
  }
  function visibility() { if (document.hidden) pause('tab hidden') }
  document.addEventListener('visibilitychange', visibility)
  onBeforeUnmount(() => { cancelMessage(); clearInterval(ticker); document.removeEventListener('visibilitychange', visibility) })
  return { screen, snapshot, session, messages, usual, history, detail, saveState, storageError, chatError, loadingMessage, question, supportOpen, simple, reducedMotion, health, measurement, active, initialize, choose, start, pause, resume, stop, openSupport, openPrivacy, send, cancelMessage, loadHistory, inspect, remove, remember, clearUsual, persist }
}
