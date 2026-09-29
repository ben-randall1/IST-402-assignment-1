<script setup>
import { computed, defineAsyncComponent, nextTick, onBeforeUnmount, ref } from 'vue'
import HotelMap from './components/HotelMap.vue'
import { useHotelSearch } from './composables/useHotelSearch'
const LegacyStays = defineAsyncComponent(() => import('./components/LegacyStays.vue'))
const view = ref('explore')
const { zipCode, state, result, errorMessage, selectedId, selectedHotel, hotels, search, cancel } = useHotelSearch()
const list = ref(null)
const infoOpen = ref(false)
const isFailure = computed(() => ['invalid', 'unresolved', 'error'].includes(state.value))
const placeLabel = computed(() => result.value?.center.locality || `ZIP ${result.value?.center.postcode}`)
const stateTitle = computed(() => ({ idle: 'Where will you go next?', loading: 'Looking around your ZIP…', invalid: 'Let’s check that ZIP code.', unresolved: 'We couldn’t locate that ZIP.', error: 'Search is temporarily unavailable.', empty: 'No nearby hotels returned.' })[state.value])
const stateDescription = computed(() => {
  if (isFailure.value) return errorMessage.value
  if (state.value === 'loading') return 'First we verify the ZIP location, then find hotels within 5 km.'
  if (state.value === 'empty') return `Geoapify returned no hotels within 5 km of ZIP ${result.value.center.postcode}. Try another ZIP code.`
  return 'Start with a U.S. ZIP code. We’ll put nearby hotels on the map so you can get a feel for the area.'
})
const observationTime = computed(() => result.value ? new Date(result.value.observed_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : '')
function formatDistance(distance) { return `${(distance / 1000).toFixed(1)} km` }
async function selectHotel(id, fromMap = false) {
  selectedId.value = id
  if (fromMap) {
    await nextTick()
    list.value?.querySelector('[aria-pressed="true"]')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }
}
onBeforeUnmount(cancel)
</script>

<template>
  <div class="app-shell">
    <header class="site-header">
      <a href="#" class="brand" aria-label="StayScout home" @click.prevent="view = 'explore'"><svg viewBox="0 0 32 36" aria-hidden="true"><path d="M16 2C8.5 2 3 7.5 3 15c0 9 13 19 13 19s13-10 13-19C29 7.5 23.5 2 16 2Z" fill="currentColor"/><path d="m10 18 6-9 6 9h-4v6h-4v-6Z" fill="#f4f3ec"/></svg>stayscout<span class="brand-period">.</span></a>
      <nav aria-label="Main navigation"><button :class="{ active: view === 'explore' }" :aria-current="view === 'explore' ? 'page' : undefined" @click="view = 'explore'">Explore hotels</button><button :class="{ active: view === 'sample' }" :aria-current="view === 'sample' ? 'page' : undefined" @click="view = 'sample'">Sample stays <span>↗</span></button></nav>
      <span class="header-note"><span></span> A little local knowledge</span>
    </header>
    <main v-if="view === 'explore'" class="explore-page">
      <section class="intro-section" aria-labelledby="page-title">
        <div class="intro-copy"><p class="eyebrow">LESS SEARCHING. MORE EXPLORING.</p><h1 id="page-title">A good stay<br>starts <em>here.</em><svg class="title-spark" viewBox="0 0 45 45" aria-hidden="true"><path d="m23 2-3 14L8 8l8 13L2 24l15 3-7 12 12-8 4 13 2-15 13 6-9-11 12-5-15-1 5-13-10 10Z" fill="currentColor"/></svg></h1><p class="intro-description">Find hotels around a U.S. ZIP code.<br>Get the lay of the land, one pin at a time.</p></div>
        <div class="search-side">
          <form class="search-card" @submit.prevent="search()" novalidate>
            <label for="zip-code">Where are you headed?</label>
            <div class="zip-input-row" :class="{ invalid: state === 'invalid' }"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></svg><div class="zip-field"><span>U.S. ZIP CODE</span><input id="zip-code" v-model="zipCode" type="text" inputmode="numeric" autocomplete="postal-code" placeholder="e.g. 16802" :aria-invalid="state === 'invalid'" aria-describedby="zip-help" :disabled="state === 'loading'"></div><button type="submit" class="search-button" :disabled="state === 'loading'">{{ state === 'loading' ? 'Searching…' : 'Find hotels' }}<span v-if="state !== 'loading'" aria-hidden="true">↗</span><span v-else class="button-spinner" aria-hidden="true"></span></button></div>
            <p id="zip-help">Five digits. A 5 km radius. A fresh place to explore.</p>
          </form>
          <div class="suggestions"><span>Try somewhere</span><button :disabled="state === 'loading'" @click="search('16802')">State College <span>↗</span></button><button :disabled="state === 'loading'" @click="search('02108')">Boston <span>↗</span></button></div>
        </div>
      </section>
      <section class="discovery-section" aria-labelledby="results-title" :aria-busy="state === 'loading'">
        <div class="section-heading"><div><p class="eyebrow">{{ result ? 'YOUR SEARCH AREA' : 'A NEW PERSPECTIVE' }}</p><h2 id="results-title">{{ result ? placeLabel : 'Small radius. Plenty to discover.' }}<span v-if="result" class="zip-badge">{{ result.center.postcode }}</span></h2></div><div class="scope-chip"><span class="radius-mini">◎</span> Within 5 km of the ZIP location</div></div>
        <div class="workspace" :class="{ 'has-results': state === 'results' }">
          <div class="list-panel" ref="list">
            <template v-if="state === 'results'"><div class="list-summary" role="status"><strong>{{ hotels.length }} hotel{{ hotels.length === 1 ? '' : 's' }}</strong><span>Nearest first</span></div><p class="list-instruction">Pick a place. Find it on the map.</p>
              <ol class="hotel-list"><li v-for="(hotel, index) in hotels" :key="hotel.place_id"><button class="hotel-card" :class="{ selected: selectedId === hotel.place_id }" :aria-pressed="selectedId === hotel.place_id" @click="selectHotel(hotel.place_id)"><span class="hotel-number">{{ String(index + 1).padStart(2, '0') }}</span><span class="hotel-details"><span class="hotel-category">HOTEL</span><strong>{{ hotel.name || 'Hotel name unavailable' }}</strong><span class="hotel-address">{{ hotel.address || 'Address not supplied' }}</span><span class="hotel-bottom"><span>{{ formatDistance(hotel.distance_meters) }} from ZIP location</span><span class="card-action">{{ selectedId === hotel.place_id ? 'On the map' : 'View on map' }} ↗</span></span></span></button></li></ol>
            </template>
            <div v-else class="state-card" :class="{ 'error-state': isFailure }" role="status" aria-live="polite"><div class="state-icon" :class="{ rotating: state === 'loading' }" aria-hidden="true">{{ isFailure ? '!' : state === 'empty' ? '○' : '⌖' }}</div><p class="eyebrow">{{ state === 'loading' ? 'SEARCH IN PROGRESS' : isFailure ? 'LET’S TRY THAT AGAIN' : 'THE START OF SOMETHING GOOD' }}</p><h3>{{ stateTitle }}</h3><p>{{ stateDescription }}</p><button v-if="state === 'error'" class="retry-button" @click="search()">Retry search ↗</button><div v-if="state === 'idle'" class="how-it-works"><div><span>01</span> Enter a ZIP</div><div><span>02</span> Explore nearby hotels</div><div><span>03</span> Connect the dots on the map</div></div></div>
          </div>
          <div class="map-panel">
            <HotelMap v-if="result" :center="result.center" :hotels="hotels" :selected-id="selectedId" @select="selectHotel($event, true)" />
            <div v-else class="map-placeholder" aria-label="Illustrative map placeholder. Search a ZIP to load real map imagery.">
              <svg class="illustration-map" viewBox="0 0 680 560" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><rect width="680" height="560" fill="#e8eadf"/><g fill="#d7dfcb"><path d="m0 0 240 0-30 160-180 20Z"/><path d="m420 380 260-60v240H490Z"/><path d="m450 0 230 0v190l-160-30Z"/><path d="m0 400 150 70-10 90H0Z"/></g><path d="M-40 270C150 370 190 140 350 220S490 420 740 240" fill="none" stroke="#cfdddd" stroke-width="38"/><g fill="none" stroke="#f8f7ef" stroke-width="13"><path d="m50-50 200 660M-20 30l450 630M390-20 210 640M-40 400 800-330M-30 540 800-300M260-30l-100 620M-10 140l770 70"/></g><g fill="none" stroke="#f7f6ed" stroke-width="5"><path d="m30 250 680 50M390 0-50 610M570 0 0 560M0 90l710 20"/></g><circle cx="352" cy="279" r="158" fill="#f5f5ec" fill-opacity=".25" stroke="#8a9c78" stroke-width="1.5" stroke-dasharray="5 8"/></svg>
              <div class="placeholder-content"><div class="compass-icon">N<span>✦</span>S</div><h3>Your next stop<br>is out there.</h3><p>{{ state === 'loading' ? 'Bringing the neighborhood into view…' : 'Search a ZIP to bring it into view.' }}</p></div><span class="illustration-label">ILLUSTRATION · LIVE MAP LOADS AFTER SEARCH</span>
            </div>
          </div>
        </div>
        <div v-if="selectedHotel" class="selection-status" role="status">Selected: <strong>{{ selectedHotel.name || 'Hotel name unavailable' }}</strong> · {{ selectedHotel.latitude.toFixed(5) }}, {{ selectedHotel.longitude.toFixed(5) }}</div>
        <div v-if="result" class="result-notes"><span>Live data via <a href="https://www.geoapify.com/" target="_blank" rel="noreferrer">Geoapify</a> · checked {{ observationTime }}</span><span>Showing up to {{ result.result_limit }} places · coverage varies<span v-if="result.limit_reached"> · result limit reached</span><span v-if="result.omitted_records"> · {{ result.omitted_records }} unusable record(s) omitted</span></span></div>
        <div class="discovery-note"><span class="note-icon" aria-hidden="true">i</span><p>A place to start, not a reservation. These are hotel locations; prices, ratings, and room availability aren’t provided.</p><button :aria-expanded="infoOpen" aria-controls="search-explainer" @click="infoOpen = !infoOpen">How search works <span>{{ infoOpen ? '−' : '+' }}</span></button></div><div v-if="infoOpen" id="search-explainer" class="search-explainer">We verify the exact U.S. ZIP with Geoapify, then search for hotels within 5 km of the returned postcode point. The center is not your position or the entire ZIP boundary. Distances are calculated in a straight line. The same hotels appear in both views; moving the map doesn’t change your search. Provider coverage varies, and the first 100 records may not include every hotel. Map imagery: © OpenStreetMap contributors.</div>
      </section>
    </main>
    <main v-else class="legacy-page"><div class="legacy-notice"><strong>Assignment 1 · supplied sample data</strong><span>All prices and bookings here are simulations using the course CSV records.</span><button @click="view = 'explore'">← Back to live discovery</button></div><LegacyStays /></main>
    <footer class="site-footer"><span>stayscout.</span><p>A little curiosity goes a long way.</p><span class="footer-tag">MADE FOR THE WAY THERE ↗</span></footer>
  </div>
</template>
