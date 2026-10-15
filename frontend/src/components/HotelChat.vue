<script setup>
import { onBeforeUnmount } from 'vue'
import { useHotelChat } from '../composables/useHotelChat'

const emit = defineEmits(['explore'])
const { question, state, errorMessage, result, ask, cancel } = useHotelChat()
const examples = [
  'Which saved hotels in ZIP 16802 have a room from October 10 to October 12, 2026, for under $250 total? Compare the total costs.',
  'Which saved hotels have rooms from October 20 to October 22, 2026?',
  'What dates and nightly rates are stored for my saved hotels?',
]
function money(cents) { return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(cents / 100) }
onBeforeUnmount(cancel)
</script>

<template>
  <main class="chat-page">
    <section class="chat-intro" aria-labelledby="chat-title">
      <p class="eyebrow">YOUR SAVED PLACES. A LITTLE MORE PERSPECTIVE.</p>
      <h1 id="chat-title">A better-informed <em>stay.</em></h1>
      <p>Compare saved hotels, dates, and costs. Ask in your own words.</p>
      <div class="chat-disclaimer"><span aria-hidden="true">◎</span> Rates and room counts are simulated course data. This assistant cannot make reservations.</div>
    </section>
    <div class="chat-layout">
      <section class="chat-conversation" aria-label="Hotel assistant">
        <form class="chat-form" @submit.prevent="ask()">
          <label for="hotel-question">What would make a good stay?</label>
          <textarea id="hotel-question" v-model="question" rows="4" maxlength="1200" placeholder="Include a ZIP, check-in and checkout dates, and your budget…" aria-describedby="question-help" :disabled="state === 'loading'" required></textarea>
          <div class="chat-form-footer"><p id="question-help">Use full dates with a year. Checkout is excluded.</p><button class="search-button" :disabled="state === 'loading'">{{ state === 'loading' ? 'Thinking…' : 'Ask StayScout' }} <span aria-hidden="true">↗</span></button></div>
        </form>
        <div class="chat-examples"><span class="eyebrow">A FEW WAYS TO START</span><button v-for="example in examples" :key="example" :disabled="state === 'loading'" @click="question = example">{{ example }} <span aria-hidden="true">↗</span></button></div>
        <div v-if="state === 'loading'" class="chat-state" role="status" aria-live="polite" aria-busy="true"><span class="button-spinner" aria-hidden="true"></span><h2>Checking your saved places…</h2><p>The assistant proposes a query, the backend checks local records, then the assistant explains the results. This can take up to two minutes.</p><button class="retry-button" @click="cancel()">Cancel waiting</button></div>
        <div v-else-if="state === 'error'" class="chat-state chat-error" role="alert"><p class="eyebrow">QUESTION NOT COMPLETED</p><h2>We couldn’t finish that answer.</h2><p>{{ errorMessage }}</p><button class="retry-button" @click="ask()">Retry question ↗</button></div>
        <article v-else-if="result" class="chat-answer" aria-live="polite">
          <p class="eyebrow">{{ state === 'no_matches' ? 'NO MATCHING LOCAL RECORDS' : 'ANSWER FROM YOUR SAVED DATA' }}</p>
          <h2>{{ state === 'no_matches' ? 'Let’s adjust the search.' : 'Here’s what the records show.' }}</h2>
          <p class="answered-question"><strong>Your question:</strong> {{ result.question }}</p>
          <p class="answer-text">{{ result.answer }}</p>
          <p class="chat-data-label">Simulated rates and availability · Local saved subset · No booking made</p>
          <p v-if="result.truncated" class="chat-warning">Results are limited to 50 rows. Narrow your question for a fuller comparison.</p>
          <p v-if="result.excluded_incomplete_stays" class="chat-warning">{{ result.excluded_incomplete_stays }} candidate stay(s) excluded because nights were missing or rooms were insufficient.</p>
          <div v-if="result.stay && result.records.length" class="chat-stay-cards">
            <article v-for="(record, index) in result.records" :key="record.hotel_id" class="chat-stay">
              <p class="eyebrow">RECORD [{{ index + 1 }}] · SIMULATED</p><h3>{{ record.name || 'Hotel name unavailable' }}</h3><p>{{ record.address || 'Address not supplied' }}</p>
              <strong>{{ money(record.total_cost_cents) }} total</strong><p>{{ record.check_in }} → {{ record.check_out }} · {{ record.nights }} night(s) · {{ record.rooms }} room(s)</p><p>At least {{ record.minimum_rooms_available }} simulated rooms on every night. Taxes and fees are not supplied.</p>
            </article>
          </div>
          <details class="chat-evidence"><summary>How this answer was found · SQL &amp; {{ result.records.length }} retrieved record(s)</summary>
            <p>Two backend model requests: question → proposed SQL → validated read-only SQLite retrieval → records and original question → answer.</p>
            <h3>1. Model-proposed SQL</h3><pre>{{ result.proposed_sql }}</pre>
            <h3>2. Records sent to the model</h3><p v-if="result.stay">The backend independently verified every night and recalculated these stay totals. Records are numbered from 1.</p><pre>{{ JSON.stringify(result.records, null, 2) }}</pre>
            <h3>3. Answer provenance</h3><p>Model: {{ result.model }} · Requests: {{ result.model_requests }} · Supporting records: {{ result.citations.length ? result.citations.join(', ') : 'none' }}</p><p>Observed: {{ result.observed_at }}</p>
          </details>
        </article>
        <div v-else class="chat-state chat-idle"><span class="state-icon" aria-hidden="true">✦</span><h2>A good question goes a long way.</h2><p>Save a few hotels in Explore, then compare their simulated nightly data here. Each question is independent; include all the details you want considered.</p></div>
      </section>
      <aside class="chat-sidebar"><p class="eyebrow">A SMALL GUIDE</p><h2>Local knowledge,<br>with the working shown.</h2><ol><li><strong>Start with saved hotels</strong><p>Use Add to Local in Explore. New saves include classroom nights for October 10–14, 2026.</p></li><li><strong>Set your priorities</strong><p>Include your dates, ZIP, room count, and whether your budget is nightly or for the whole stay.</p></li><li><strong>Check the details</strong><p>Compare the answer with its supporting records. AI can misunderstand a question; missing nights never count as available.</p></li></ol><button class="retry-button" @click="emit('explore')">Explore &amp; save hotels ↗</button><p class="chat-privacy">Your question and limited saved hotel records are sent to the configured OpenRouter model. Keep personal information out of questions.</p></aside>
    </div>
  </main>
</template>

<style scoped>
.chat-page{padding:45px 0 50px}.chat-intro{max-width:820px;margin-bottom:30px}.chat-intro h1{font:400 clamp(36px,4.5vw,62px)/1.1 Georgia,serif;letter-spacing:-1.7px;margin:16px 0}.chat-intro h1 em{color:#597047}.chat-intro>p:not(.eyebrow){font-size:16px;color:#707b69;line-height:1.7}.chat-disclaimer{display:flex;gap:10px;align-items:center;margin-top:21px;color:#667553;font-size:12px;line-height:1.7}.chat-layout{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:30px;align-items:start}.chat-conversation{min-width:0}.chat-form{padding:25px;background:#eeefe5;border:1px solid #dfe2d5;border-radius:14px}.chat-form label{font:700 17px Manrope,sans-serif}.chat-form textarea{display:block;resize:vertical;min-height:110px;width:100%;font:inherit;font-size:14px;line-height:1.7;background:#fffefb;color:#283e33;padding:16px;border:1px solid #ccd6c2;border-radius:8px;margin:17px 0}.chat-form textarea:focus-visible{outline:2px solid #78895c;outline-offset:2px}.chat-form-footer{display:flex;gap:16px;align-items:center;justify-content:space-between}.chat-form-footer p{font-size:10px;color:#6c7763;line-height:1.7}.chat-examples{margin:23px 0;display:grid;gap:9px}.chat-examples>.eyebrow{margin-bottom:4px}.chat-examples button{display:flex;justify-content:space-between;gap:15px;text-align:left;background:#fffefb;border:1px solid #e0e3d6;border-radius:8px;padding:13px 16px;font-size:12px;line-height:1.6}.chat-examples button:hover{background:#edf1e4}.chat-state,.chat-answer{border:1px solid #d8dfcd;background:#fffefb;border-radius:14px;padding:26px}.chat-state h2,.chat-answer h2{font:400 28px Georgia,serif;margin:12px 0 16px}.chat-state p{font-size:13px;line-height:1.8;color:#6d7963}.chat-state .button-spinner{display:inline-block;border-color:#cbd5c2;border-top-color:#36593d}.chat-error{background:#fff6ed;border-color:#dab69d}.chat-error .eyebrow{color:#935637}.chat-idle .state-icon{margin-bottom:16px}.answer-text{white-space:pre-wrap;font-size:14px;line-height:1.9;overflow-wrap:anywhere}.answered-question{font-size:12px;background:#f2f4eb;padding:13px;border-radius:6px;line-height:1.7;margin-bottom:18px}.chat-data-label{font-size:10px;color:#5e7450;margin-top:20px;padding-top:16px;border-top:1px solid #e1e6d9}.chat-warning{padding:10px;background:#fff2d4;font-size:12px;margin-top:12px;line-height:1.7}.chat-stay-cards{display:grid;gap:12px;margin-top:20px}.chat-stay{padding:17px;background:#f2f5ec;border:1px solid #d7e0cc;border-radius:8px}.chat-stay h3{font-size:16px;margin:8px 0}.chat-stay p:not(.eyebrow){font-size:11px;line-height:1.8;color:#697b5a}.chat-stay>strong{display:block;font-size:20px;margin:15px 0 8px}.chat-evidence{border-top:1px solid #dce2d3;padding-top:20px;margin-top:22px}.chat-evidence summary{cursor:pointer;font-weight:700;font-size:12px;line-height:1.7}.chat-evidence p{font-size:11px;line-height:1.8;margin:13px 0;overflow-wrap:anywhere}.chat-evidence h3{font-size:12px;margin-top:18px}.chat-evidence pre{padding:15px;background:#243c30;color:#eff4e8;border-radius:7px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:11px;line-height:1.8;max-height:370px;overflow:auto}.chat-sidebar{background:#e9eddf;border:1px solid #dce3d2;border-radius:14px;padding:26px}.chat-sidebar h2{font:400 26px/1.25 Georgia,serif;letter-spacing:-.5px;margin:16px 0 25px}.chat-sidebar ol{margin:0;padding-left:20px}.chat-sidebar li{padding-left:6px;margin:0 0 23px}.chat-sidebar li::marker{color:#82956f;font-size:12px}.chat-sidebar li strong{font-size:12px}.chat-sidebar li p,.chat-privacy{font-size:11px;color:#6f7e61;line-height:1.9;margin-top:8px}.chat-privacy{border-top:1px solid #d2dbc5;padding-top:18px;margin-top:24px}.chat-sidebar .retry-button{margin-top:0}
@media(max-width:900px){.chat-layout{grid-template-columns:minmax(0,1fr)}.chat-sidebar{max-width:none}.chat-sidebar h2 br{display:none}}@media(max-width:580px){.chat-page{padding-top:30px}.chat-intro .eyebrow{font-size:8px}.chat-intro h1{font-size:38px}.chat-form,.chat-state,.chat-answer{padding:18px}.chat-form-footer{align-items:stretch;flex-direction:column}.chat-form-footer .search-button{align-self:flex-end}.chat-intro>p:not(.eyebrow){font-size:14px}}
</style>
