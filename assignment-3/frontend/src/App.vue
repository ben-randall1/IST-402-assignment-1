<script setup>
import { onMounted } from 'vue'
import SupportPanel from './components/SupportPanel.vue'
import { usePractice } from './composables/usePractice.js'
const p = usePractice()
const { screen, snapshot, session, messages, usual, history, detail, saveState, storageError, chatError, loadingMessage, question, supportOpen, simple, reducedMotion, health, measurement } = p
onMounted(p.initialize)
const seconds = ms => `${((ms ?? 0) / 1000).toFixed(2)} s`
const date = value => new Date(value).toLocaleString()
function home() { p.stop(); screen.value = 'home' }
function back() { screen.value = snapshot.value.status === 'paused' ? 'paused' : snapshot.value.status === 'ready' && session.value ? 'ready' : 'home' }
function leaveSupport() { supportOpen.value = false; p.stop() }
</script>
<template>
  <div class="app" :class="{ simple }">
    <header class="site-header">
      <button class="brand" @click="home">a little space<span>Coursework prototype</span></button>
      <nav aria-label="Always available"><button class="support-link" @click="p.openSupport">Crisis support</button><button @click="p.stop">Leave practice</button></nav>
    </header>
    <div class="environment" v-if="health?.mode === 'fixture'">MOCK MODEL MODE · Fictional responses · Temporary SQLite database · No provider calls</div>
    <div class="environment" v-else>Fictional scenarios only · Local, single-user demonstration · Not a support service</div>
    <main id="main" :data-screen="screen" :data-session="session?.session_id" :data-status="snapshot.status">
      <div class="utility"><button @click="simple = !simple" :aria-pressed="simple">{{ simple ? 'Show full view' : 'Less on screen' }}</button><button @click="p.loadHistory">Local history</button><button @click="p.openPrivacy">Privacy &amp; limits</button></div>
      <div v-if="storageError" class="notice warning" role="status">{{ storageError }} <button v-if="session" @click="p.persist()">Retry checkpoint</button></div>
      <template v-if="screen === 'home'">
        <p class="eyebrow">A small, optional practice</p><h1>Choose a little space.</h1>
        <p class="intro">One short, fixed breathing sequence. Start when you choose, pause at any point, or leave without explaining.</p>
        <section class="skill-card" aria-labelledby="skill-title"><div><span class="eyebrow">About 60 seconds · Six rounds</span><h2 id="skill-title">Paced breathing</h2><p>In for 4 seconds. Out for 6 seconds. Follow only if comfortable; return to normal breathing or stop whenever you want.</p></div><button class="primary" @click="p.choose">Choose paced breathing</button></section>
        <section v-if="usual" class="notice"><h2>Your saved choice</h2><p>You explicitly saved paced breathing as your usual choice. It will never start automatically; saving it does not mean it helped.</p><div class="actions"><button @click="p.choose">Choose my usual</button><button @click="p.clearUsual">Forget usual choice</button></div></section>
        <p class="quiet extra">You do not need to describe a feeling or share a message to begin. This demonstration does not diagnose, provide therapy, or assess safety.</p>
      </template>
      <template v-else-if="screen === 'ready'">
        <p class="eyebrow">You chose paced breathing</p><h1>At your own pace.</h1><p class="intro">Six rounds: breathe in for 4 seconds, then out for 6. No breath holding. Keep your eyes open if you prefer. Stop if uncomfortable.</p>
        <div class="actions"><button class="primary" @click="p.start">Start the 60-second practice</button><button @click="home">Choose later</button></div>
        <section class="orientation extra" aria-labelledby="orientation-title"><h2 id="orientation-title">Optional orientation</h2><p class="extra">A model can select an explanation from reviewed wording using your message, up to four messages from this session, and your explicitly saved usual choice. It cannot change the steps or timer.</p>
          <p class="notice" v-if="!health?.model_configured && health?.mode !== 'fixture'">The model is not configured or is unavailable. You can start the fixed practice now.</p>
          <p class="quiet">Use fictional text only. In normal mode, sending stores this conversation locally and sends the listed context to OpenRouter. Mock mode uses only local fixtures. <button class="text-button" @click="p.openPrivacy">Read privacy &amp; limits</button></p>
          <ol class="conversation" aria-label="Saved conversation"><li v-for="message in messages" :key="message.message_id" :class="message.role"><span class="eyebrow">{{ message.role === 'user' ? 'Fictional message' : message.source === 'model' ? 'Model-selected reviewed response' : 'Application / mock response' }}</span><p>{{ message.content }}</p><small v-if="message.model_id">{{ message.model_id }} · {{ message.response_code }}</small></li></ol>
          <form @submit.prevent="p.send"><label for="question">Optional fictional message</label><textarea id="question" v-model="question" maxlength="500" rows="3" placeholder="For example: What do the counts mean?" :disabled="loadingMessage"></textarea><span class="quiet">{{ question.length }}/500</span><div class="actions"><button type="submit" :disabled="loadingMessage">{{ loadingMessage ? 'Waiting for orientation…' : 'Send fictional message' }}</button><button type="button" v-if="loadingMessage" @click="p.cancelMessage">Cancel reply</button></div></form>
          <p v-if="chatError" class="notice warning" role="alert">{{ chatError }} Start remains available above. Resending is an explicit new attempt.</p>
        </section>
      </template>
      <template v-else-if="screen === 'practice'">
        <section class="practice" aria-label="Paced breathing"><p class="eyebrow">Round {{ snapshot.round }} of 6</p><h1 aria-live="polite">{{ snapshot.phase === 'inhale' ? 'Breathe in' : 'Breathe out' }}</h1>
          <div class="cue-wrap"><div class="cue" :class="{ still: reducedMotion }" :style="{ transform: `scale(${reducedMotion ? 1 : snapshot.cue_scale})` }"><span aria-hidden="true">{{ snapshot.count }}</span></div></div>
          <p>{{ snapshot.phase === 'inhale' ? 'In for 4 seconds' : 'Out for 6 seconds' }}</p><p class="quiet extra">Follow only if comfortable. Normal breathing and stopping are always okay.</p><div class="actions centered"><button class="primary" @click="p.pause()">Pause</button><button @click="p.stop">Stop practice</button><button @click="reducedMotion = !reducedMotion" :aria-pressed="reducedMotion">{{ reducedMotion ? 'Use expanding cue' : 'Use still cue' }}</button></div></section>
      </template>
      <template v-else-if="screen === 'paused'">
        <p class="eyebrow">Paused · No countdown</p><h1>Take your time.</h1><p class="intro">Resume when you choose. The interrupted round will restart from its inhale. Extra active time and paused time are recorded separately.</p><div class="actions"><button class="primary" @click="p.resume">Resume practice</button><button @click="p.stop">Stop practice</button></div>
      </template>
      <template v-else-if="screen === 'ended'">
        <p class="eyebrow">Six rounds ended</p><h1>The sequence is complete.</h1><p class="intro">You can return to normal breathing and leave. Completion is a timing record, not an assessment of how you feel.</p>
        <dl class="metrics" v-if="measurement" :data-observed-sequence-ms="measurement.observed_sequence_ms" :data-active-ms="measurement.active_ms" :data-setup-ms="measurement.setup_ms"><div><dt>Observed sequence, including pauses</dt><dd>{{ seconds(measurement.observed_sequence_ms) }}</dd></div><div><dt>Active time, including repeated rounds</dt><dd>{{ seconds(measurement.active_ms) }}</dd></div><div><dt>Paused time</dt><dd>{{ seconds(measurement.paused_ms) }}</dd></div><div><dt>Repeated active time</dt><dd>{{ seconds(measurement.replay_ms) }}</dd></div><div><dt>Choice to first cue</dt><dd>{{ seconds(measurement.setup_ms) }}</dd></div></dl>
        <div class="actions"><button @click="p.remember()" :disabled="!session || saveState !== 'saved'">Save as my usual choice</button><button class="primary" @click="home">Return to choices</button></div><p v-if="usual" role="status">Paced breathing is saved as your usual choice. You can forget it from the home screen.</p>
      </template>
      <template v-else-if="screen === 'stopped'">
        <p class="eyebrow">You are free to leave</p><h1>Stopped here.</h1><p class="intro">No explanation is needed. Nothing will restart automatically.</p><div class="actions"><button class="primary" @click="home">Return to choices</button><button @click="p.loadHistory">Review local history</button></div>
      </template>
      <template v-else-if="screen === 'history'">
        <p class="eyebrow">Stored on this computer</p><h1>Local history.</h1><p class="quiet">Latest 50 sessions. Reloading never restarts a practice. Checkpoints may be incomplete after a crash or save failure.</p><button @click="back">Back to choices or paused practice</button>
        <p v-if="!history.length">No saved sessions are available.</p><div class="history-grid"><button v-for="item in history" :key="item.session_id" class="history-card" @click="p.inspect(item.session_id)"><strong>Paced breathing · {{ item.status }}</strong><span>{{ date(item.started_at) }}</span><span>{{ seconds(item.active_ms) }} active · {{ item.message_count }} messages</span></button></div>
        <section v-if="detail" class="detail"><h2>Saved session · {{ detail.session.status }}</h2><p class="quiet">{{ detail.session.session_id }}</p><dl class="metrics"><div><dt>Active time</dt><dd>{{ seconds(detail.session.active_ms) }}</dd></div><div><dt>Paused time</dt><dd>{{ seconds(detail.session.paused_ms) }}</dd></div></dl><ol class="conversation"><li v-for="m in detail.messages" :key="m.message_id"><span class="eyebrow">{{ m.role }} · {{ m.source }}</span><p>{{ m.content }}</p><small>{{ m.model_id || 'No live model' }}</small></li></ol><p v-for="attempt in detail.attempts.filter(a => a.status !== 'succeeded')" :key="attempt.user_message_id" class="notice">Message attempt: {{ attempt.status }}{{ attempt.error_status ? ` (HTTP ${attempt.error_status})` : '' }}. No successful answer is claimed.</p><details><summary>Saved timing checkpoint</summary><pre>{{ JSON.stringify(detail.session.progress, null, 2) }}</pre></details><div class="actions"><button @click="p.remember(detail.session.session_id)">Explicitly save this skill as usual</button><button @click="p.remove(detail.session.session_id)">Delete this session and messages</button></div></section>
      </template>
      <template v-else-if="screen === 'privacy'">
        <p class="eyebrow">Privacy &amp; limits</p><h1>A local coursework prototype.</h1><p>This application is only for fictional scenarios. It is not therapy, diagnosis, a safety assessment, or monitored support. It cannot contact anyone for you.</p><p>The SQLite database stores session timestamps, timing checkpoints, message text, response identifiers and model IDs. A usual choice is stored only when you explicitly save it. Text is not used to infer a diagnosis or simplification preference.</p><p>The local database is unencrypted and has no account isolation. Anyone with access to this computer may access it. Do not enter real sensitive information. Run only on localhost; this is not a multi-user deployment.</p><p>Optional messages send your current fictional message, up to four messages from that session, reviewed skill and response content, and your explicit usual preference to OpenRouter and its model provider. Their own processing policies apply. Local deletion does not delete provider-side records. API credentials stay on the backend.</p><p>You can delete a local session and its messages in Local history and forget your usual choice on the home screen. Failed model attempts remain labeled as failures. The practice and crisis information do not require a model response.</p><button @click="back">Back to choices or paused practice</button>
      </template>
      <footer><span v-if="session" role="status">Local checkpoint: {{ saveState === 'saved' ? 'saved' : saveState === 'saving' ? 'saving…' : 'not saved' }}</span><span v-else>Fictional coursework · No monitoring</span><span>Stop whenever you choose.</span></footer>
    </main>
    <SupportPanel :open="supportOpen" @close="supportOpen = false" @leave="leaveSupport" />
  </div>
</template>
