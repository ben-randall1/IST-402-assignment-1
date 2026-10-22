// The clock owns the fixed 4–6 sequence. It never waits for network or model output.
export class PracticeClock {
  constructor(now = () => performance.now()) {
    this.now = now
    this.state = 'ready'
    this.offset = 0
    this.runningTotal = 0
    this.pausedTotal = 0
    this.replay = 0
    this.trace = []
    this.started = null
    this.finished = null
    this.runAt = null
    this.pauseAt = null
    this.lastPhase = null
  }
  start() {
    if (this.state !== 'ready') return
    this.state = 'active'
    this.started = this.runAt = this.now()
    this.trace.push({ event: 'start', at_ms: 0, planned_ms: 0 })
    return this.snapshot()
  }
  plannedAt(now) { return this.offset + (this.state === 'active' ? now - this.runAt : 0) }
  snapshot() {
    const now = this.now()
    let planned = this.plannedAt(now)
    if (this.state === 'active' && planned >= 60000) {
      this.runningTotal += now - this.runAt
      this.offset = 60000
      this.state = 'completed'
      this.finished = now
      planned = 60000
      this.trace.push({ event: 'sequence_ended', at_ms: now - this.started, planned_ms: planned })
    }
    const position = Math.min(planned, 59999)
    const phaseMs = position % 10000
    const phase = phaseMs < 4000 ? 'inhale' : 'exhale'
    if (this.state === 'active' && phase !== this.lastPhase) {
      this.lastPhase = phase
      this.trace.push({ event: phase, round: Math.floor(position / 10000) + 1, at_ms: now - this.started, planned_ms: planned })
    }
    return {
      status: this.state, phase, round: Math.floor(position / 10000) + 1,
      count: Math.max(1, Math.ceil(((phase === 'inhale' ? 4000 : 10000) - phaseMs) / 1000)),
      cue_scale: phase === 'inhale' ? 0.76 + phaseMs / 4000 * 0.24 : 1 - (phaseMs - 4000) / 6000 * 0.24,
      planned_ms: Math.min(60000, Math.round(planned)),
      active_ms: Math.round(this.runningTotal + (this.state === 'active' ? now - this.runAt : 0)),
      paused_ms: Math.round(this.pausedTotal + (this.state === 'paused' ? now - this.pauseAt : 0)),
      replay_ms: Math.round(this.replay),
      elapsed_ms: this.started === null ? 0 : Math.round((this.finished ?? now) - this.started),
      trace: this.trace.map(event => ({ ...event })),
    }
  }
  pause(reason = 'user') {
    this.snapshot()
    if (this.state !== 'active') return this.snapshot()
    const now = this.now()
    this.offset += now - this.runAt
    this.runningTotal += now - this.runAt
    this.pauseAt = now
    this.state = 'paused'
    this.trace.push({ event: 'pause', reason, at_ms: now - this.started, planned_ms: this.offset })
    return this.snapshot()
  }
  resume() {
    if (this.state !== 'paused') return this.snapshot()
    const now = this.now()
    this.pausedTotal += now - this.pauseAt
    const partial = this.offset % 10000
    this.replay += partial
    this.offset -= partial
    this.runAt = now
    this.lastPhase = null
    this.state = 'active'
    this.trace.push({ event: 'resume_round', at_ms: now - this.started, replay_ms: partial, planned_ms: this.offset })
    return this.snapshot()
  }
  stop() {
    this.snapshot()
    if (['completed', 'stopped'].includes(this.state)) return this.snapshot()
    const now = this.now()
    if (this.state === 'active') { this.offset += now - this.runAt; this.runningTotal += now - this.runAt }
    if (this.state === 'paused') this.pausedTotal += now - this.pauseAt
    this.state = 'stopped'
    this.finished = now
    this.trace.push({ event: 'stop', at_ms: this.started === null ? 0 : now - this.started })
    return this.snapshot()
  }
}
