import test from 'node:test'
import assert from 'node:assert/strict'
import { PracticeClock } from './practiceClock.js'
function setup() { let now=0; const clock=new PracticeClock(()=>now); return { clock, at(ms) { now=ms; return clock.snapshot() } } }
test('six full rounds have fixed phase boundaries and complete with observed delay',()=>{
  const {clock,at}=setup(); clock.start()
  for(let round=0;round<6;round++) {
    assert.equal(at(round*10000).phase,'inhale')
    assert.equal(at(round*10000+3999).phase,'inhale')
    assert.equal(at(round*10000+4000).phase,'exhale')
    assert.equal(at(round*10000+9999).status,'active')
  }
  const end=at(60027); assert.equal(end.status,'completed'); assert.equal(end.active_ms,60027); assert.equal(end.planned_ms,60000)
  assert.equal(end.trace.filter(e=>['inhale','exhale'].includes(e.event)).length,12)
  assert.equal(at(90000).active_ms,60027)
})
test('pause excludes waiting and explicitly resumes the interrupted round',()=>{
  const {clock,at}=setup();clock.start();at(4500);clock.pause('tab hidden')
  assert.equal(at(15000).planned_ms,4500);assert.equal(at(15000).paused_ms,10500)
  clock.resume();assert.equal(at(15000).phase,'inhale');assert.equal(at(15000).replay_ms,4500)
  const end=at(75000);assert.equal(end.status,'completed');assert.equal(end.active_ms,64500);assert.equal(end.paused_ms,10500)
})
test('stop freezes time from ready, active and paused and cannot restart',()=>{
  for(const state of ['ready','active','paused']){
    const {clock,at}=setup();if(state!=='ready'){clock.start();at(1234)}if(state==='paused')clock.pause()
    const stopped=clock.stop();assert.equal(stopped.status,'stopped');assert.equal(at(20000).active_ms,stopped.active_ms)
    clock.start();assert.equal(clock.snapshot().status,'stopped')
  }
})
test('delayed callback records actual elapsed time rather than claiming exactly 60 seconds',()=>{
  const {clock,at}=setup();clock.start();const result=at(61050);assert.equal(result.active_ms,61050);assert.equal(result.elapsed_ms,61050)
})
