<script setup>
import { ref, watch, nextTick } from 'vue'
const props = defineProps({ open: Boolean })
const emit = defineEmits(['close', 'leave'])
const dialog = ref(null)
let previousFocus
watch(() => props.open, async value => {
  await nextTick()
  if (value && !dialog.value.open) { previousFocus = document.activeElement; dialog.value.showModal(); dialog.value.querySelector('button')?.focus() }
  else if (!value && dialog.value.open) { dialog.value.close(); previousFocus?.focus() }
})
</script>
<template>
  <dialog ref="dialog" aria-labelledby="support-title" @cancel.prevent="emit('close')">
    <div class="dialog-head"><span class="eyebrow">Always available · United States</span><div class="dialog-actions"><button @click="emit('close')">Close</button><button @click="emit('leave')">Leave practice</button></div></div>
    <h2 id="support-title">Crisis support</h2>
    <p>If you may act on thoughts of harming yourself or are in immediate danger, contact emergency services or go to an emergency department.</p>
    <p>In the U.S., call or text 988 or use its online chat for suicide and crisis support.</p>
    <div class="actions"><a class="button primary" href="tel:988?oai_link_source=model_response_hotline">Call 988</a><a class="button" href="sms:988?oai_link_source=model_response_hotline">Text 988</a><a class="button" href="https://988lifeline.org/chat/?oai_link_source=model_response_hotline" target="_blank" rel="noopener noreferrer">988 online chat ↗</a></div>
    <p>Outside the U.S., contact a local crisis or emergency service. Phone, text and online actions depend on your device and connection.</p>
    <div class="notice">This fictional coursework prototype is not monitored and cannot contact anyone for you. These contacts are provided by external services. Opening this panel never sends your conversation.</div>
    <p>You can stop or leave without explaining. A paused practice will stay paused when this panel closes.</p>
    <div class="actions"><button @click="emit('close')">Close support information</button></div>
  </dialog>
</template>
