<script setup>
import { onMounted, ref } from 'vue'

const apiUrl = '/api'
const zipCode = ref('16802')
const location = ref(null)
const zipMessage = ref('Enter a five-digit U.S. ZIP code to find its returned location.')
const zipLoading = ref(false)
const hasZipResult = ref(false)
const searchQuery = ref('Harbor')
const stays = ref([])
const users = ref([])
const bookings = ref([])
const selectedUserId = ref('')
const message = ref('Search by hotel name to see its available stays.')
const bookingMessage = ref('Choose a traveler, then use a Book this stay button.')
const historyMessage = ref('Choose a traveler to view their booking history.')
const loading = ref(false)
const hasSearched = ref(false)

async function getJson(path, options = {}) {
  const response = await fetch(`${apiUrl}${path}`, options)
  const payload = await response.json()
  if (!response.ok) throw new Error(payload.detail || 'The server could not complete that request.')
  return payload
}

async function lookupZip(zip = zipCode.value, endpoint = null) {
  const enteredZip = zip.trim()
  location.value = null
  hasZipResult.value = false

  if (!/^\d{5}$/.test(enteredZip)) {
    zipMessage.value = 'Enter a five-digit U.S. ZIP code, including any leading zero.'
    return
  }

  zipLoading.value = true
  zipMessage.value = `Looking up ZIP code ${enteredZip}…`
  try {
    location.value = await getJson(endpoint || `/zip-location?zip_code=${encodeURIComponent(enteredZip)}`)
    hasZipResult.value = true
    zipMessage.value = `Verified location returned for ZIP code ${location.value.postcode}.`
  } catch (error) {
    zipMessage.value = error.message
  } finally {
    zipLoading.value = false
  }
}

function lookupDemoZip() {
  zipCode.value = '16802'
  lookupZip('16802', '/demo/zip-location')
}

async function loadUsers() {
  try {
    users.value = await getJson('/users')
    if (users.value.length) {
      selectedUserId.value = users.value[0].user_id
      await loadHistory()
    }
  } catch (error) {
    historyMessage.value = error.message
  }
}

async function search() {
  const query = searchQuery.value.trim()
  if (!query) {
    stays.value = []
    hasSearched.value = false
    message.value = 'Enter a hotel name before searching.'
    return
  }

  loading.value = true
  try {
    const result = await getJson(`/stays?query=${encodeURIComponent(query)}`)
    stays.value = result.stays
    hasSearched.value = true
    message.value = result.count
      ? `${result.count} available stay${result.count === 1 ? '' : 's'} found for “${result.query}”.`
      : `No hotel stays match “${result.query}”. Try another hotel name.`
  } catch (error) {
    stays.value = []
    hasSearched.value = false
    message.value = error.message
  } finally {
    loading.value = false
  }
}

async function createBooking(tripId) {
  if (!selectedUserId.value) return
  bookingMessage.value = 'Creating booking…'
  try {
    const result = await getJson('/bookings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: selectedUserId.value, trip_id: tripId }),
    })
    bookingMessage.value = `${result.message} ID: ${result.booking_id}`
    await loadHistory()
  } catch (error) {
    bookingMessage.value = error.message
  }
}

async function loadHistory() {
  if (!selectedUserId.value) return
  try {
    bookings.value = await getJson(`/bookings?user_id=${encodeURIComponent(selectedUserId.value)}`)
    historyMessage.value = bookings.value.length
      ? `${bookings.value.length} booking${bookings.value.length === 1 ? '' : 's'} in this history.`
      : 'No bookings exist for this traveler yet.'
  } catch (error) {
    historyMessage.value = error.message
  }
}

async function cancelBooking(bookingId) {
  try {
    await getJson(`/bookings/${bookingId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'cancelled' }),
    })
    historyMessage.value = `Booking ${bookingId} was cancelled and remains in history.`
    await loadHistory()
  } catch (error) {
    historyMessage.value = error.message
  }
}

async function deleteBooking(bookingId) {
  try {
    await getJson(`/bookings/${bookingId}`, { method: 'DELETE' })
    historyMessage.value = `Test booking ${bookingId} was deleted.`
    await loadHistory()
  } catch (error) {
    historyMessage.value = error.message
  }
}

onMounted(loadUsers)
</script>

<template>
  <div class="page-shell">
    <section class="hero" aria-labelledby="page-title">
      <p class="eyebrow">Travel planning, made simple</p>
      <h1 id="page-title">Find and book your next hotel stay</h1>
      <p class="intro">Search available stays, make a simulated booking, and review your travel history.</p>

      <section class="zip-panel" aria-labelledby="zip-title" aria-live="polite">
        <div class="zip-heading">
          <div>
            <p class="eyebrow">Public API demonstration</p>
            <h2 id="zip-title">ZIP location lookup</h2>
          </div>
          <button class="demo-button" type="button" :disabled="zipLoading" @click="lookupDemoZip">
            Look up ZIP 16802
          </button>
        </div>
        <form class="zip-search" @submit.prevent="lookupZip()">
          <label for="zip-search">Five-digit U.S. ZIP code</label>
          <div class="search-row">
            <input id="zip-search" v-model="zipCode" name="zip-search" inputmode="numeric" maxlength="5" placeholder="e.g., 16802" autocomplete="postal-code" />
            <button type="submit" :disabled="zipLoading">{{ zipLoading ? 'Looking up…' : 'Look up ZIP' }}</button>
          </div>
        </form>
        <p class="zip-message">{{ zipMessage }}</p>
        <div v-if="hasZipResult" class="table-wrap location-table-wrap">
          <table class="location-table">
            <thead>
              <tr>
                <th scope="col">ZIP code</th>
                <th scope="col">Country code</th>
                <th scope="col">Locality</th>
                <th scope="col">Latitude</th>
                <th scope="col">Longitude</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{{ location.postcode }}</td>
                <td>{{ location.country_code.toUpperCase() }}</td>
                <td>{{ location.locality || '—' }}</td>
                <td>{{ location.latitude }}</td>
                <td>{{ location.longitude }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <form class="search-panel" @submit.prevent="search">
        <label for="hotel-search">Hotel name</label>
        <div class="search-row">
          <input id="hotel-search" v-model="searchQuery" name="hotel-search" placeholder="e.g., Harbor Lantern" autocomplete="off" />
          <button type="submit" :disabled="loading">{{ loading ? 'Searching…' : 'Search' }}</button>
        </div>
      </form>
    </section>

    <section class="booking-panel" aria-labelledby="booking-title">
      <div>
        <p class="section-kicker">Simulated booking</p>
        <h2 id="booking-title">Choose a traveler</h2>
      </div>
      <div class="traveler-control">
        <label for="traveler">Demo traveler</label>
        <select id="traveler" v-model="selectedUserId" @change="loadHistory">
          <option v-for="user in users" :key="user.user_id" :value="user.user_id">
            {{ user.display_name }} ({{ user.user_id }})
          </option>
        </select>
      </div>
      <p class="panel-message">{{ bookingMessage }}</p>
    </section>

    <section class="results" aria-live="polite" aria-labelledby="results-title">
      <div class="results-heading">
        <h2 id="results-title">Available hotel stays</h2>
        <p>{{ message }}</p>
      </div>

      <div v-if="hasSearched && stays.length" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th scope="col">Hotel</th>
              <th scope="col">City</th>
              <th scope="col">Trip</th>
              <th scope="col">Check-in</th>
              <th scope="col">Check-out</th>
              <th scope="col">Nights</th>
              <th scope="col">Stay price</th>
              <th scope="col">Booking</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="stay in stays" :key="stay.trip_id">
              <td>{{ stay.hotel_name }}</td>
              <td>{{ stay.city }}, {{ stay.state }}</td>
              <td>{{ stay.trip_name }}</td>
              <td>{{ stay.check_in }}</td>
              <td>{{ stay.check_out }}</td>
              <td>{{ stay.nights }}</td>
              <td>{{ stay.stay_price }}</td>
              <td><button class="small-button" type="button" @click="createBooking(stay.trip_id)">Book this stay</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="history" aria-live="polite" aria-labelledby="history-title">
      <div class="results-heading">
        <h2 id="history-title">Booking history</h2>
        <button class="secondary-button" type="button" @click="loadHistory">Refresh history</button>
      </div>
      <p class="history-message">{{ historyMessage }}</p>
      <div v-if="bookings.length" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th scope="col">Booking ID</th>
              <th scope="col">Hotel stay</th>
              <th scope="col">Dates</th>
              <th scope="col">Booked on</th>
              <th scope="col">Status</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="booking in bookings" :key="booking.booking_id">
              <td>{{ booking.booking_id }}</td>
              <td>{{ booking.hotel_name }} — {{ booking.trip_name }}</td>
              <td>{{ booking.check_in }} to {{ booking.check_out }}</td>
              <td>{{ booking.booked_on }}</td>
              <td><span class="status" :class="booking.status">{{ booking.status }}</span></td>
              <td class="action-cell">
                <button v-if="booking.status === 'confirmed'" class="secondary-button" type="button" @click="cancelBooking(booking.booking_id)">Cancel</button>
                <button class="delete-button" type="button" @click="deleteBooking(booking.booking_id)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped>
:root { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #1c2a39; background: #f7f6f2; }
* { box-sizing: border-box; }
body { margin: 0; }
button, input, select { font: inherit; }
.page-shell { width: min(100% - 2rem, 980px); margin: 0 auto; padding: 4.5rem 0; }
.hero { border-radius: 20px; padding: clamp(2rem, 7vw, 5rem); color: #fff; background: linear-gradient(120deg, #103b4a, #176a77); box-shadow: 0 16px 45px rgb(16 59 74 / 18%); }
.eyebrow { margin: 0 0 .65rem; color: #cdebef; font-size: .78rem; font-weight: 750; letter-spacing: .11em; text-transform: uppercase; }
h1 { max-width: 640px; margin: 0; font-family: Georgia, serif; font-size: clamp(2.4rem, 6vw, 4.8rem); line-height: 1; }
.intro { margin: 1rem 0 2rem; font-size: 1.1rem; color: #e4f5f7; }
.zip-panel { max-width: 760px; margin: 0 0 1.2rem; padding: 1.1rem; border: 1px solid #95cdd2; border-radius: 13px; background: #f8ffff; color: #1c2a39; }
.zip-heading { display: flex; align-items: end; justify-content: space-between; gap: 1rem; }
.zip-heading .eyebrow { margin-bottom: .3rem; color: #176a77; }
.zip-heading h2 { font-size: 1.3rem; }
.demo-button { flex: 0 0 auto; padding: .6rem .8rem; background: #176a77; }
.demo-button:hover { background: #103b4a; }
.zip-search { margin-top: 1rem; }
.zip-message { margin: .85rem 0 0; color: #405460; }
.location-table-wrap { margin-top: .85rem; box-shadow: none; }
.location-table { min-width: 610px; }
.search-panel { max-width: 620px; padding: 1.1rem; border-radius: 13px; background: #fff; color: #1c2a39; }
label { display: block; margin: 0 0 .45rem; font-size: .85rem; font-weight: 700; }
.search-row { display: flex; gap: .7rem; }
input { width: 100%; min-width: 0; padding: .77rem .85rem; border: 1px solid #adc5ca; border-radius: 8px; color: #1c2a39; }
input:focus, select:focus { outline: 3px solid #7ad6da; outline-offset: 1px; }
button { padding: .77rem 1.1rem; border: 0; border-radius: 8px; background: #e46e46; color: white; cursor: pointer; font-weight: 750; }
button:hover { background: #c85131; }
button:disabled { cursor: wait; opacity: .7; }
.results { margin-top: 3rem; }
.booking-panel { display: grid; grid-template-columns: 1fr minmax(230px, .8fr); gap: 1rem 2rem; align-items: end; margin-top: 2rem; padding: 1.4rem; border: 1px solid #dbe3e4; border-radius: 12px; background: #fff; }
.section-kicker { margin: 0 0 .35rem; color: #176a77; font-size: .78rem; font-weight: 750; letter-spacing: .08em; text-transform: uppercase; }
.traveler-control label { margin-bottom: .4rem; }
select { width: 100%; padding: .77rem .85rem; border: 1px solid #adc5ca; border-radius: 8px; background: #fff; color: #1c2a39; }
.panel-message { grid-column: 1 / -1; margin: 0; color: #536575; }
.results-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 1rem; margin-bottom: .9rem; }
h2 { margin: 0; font-size: 1.45rem; }
.results-heading p { margin: 0; color: #536575; }
.table-wrap { overflow-x: auto; background: #fff; border: 1px solid #dbe3e4; border-radius: 12px; box-shadow: 0 5px 18px rgb(22 45 54 / 7%); }
table { width: 100%; border-collapse: collapse; min-width: 940px; text-align: left; }
th, td { padding: 1rem; border-bottom: 1px solid #e4eaeb; }
th { background: #eff7f7; font-size: .82rem; letter-spacing: .02em; }
tbody tr:last-child td { border-bottom: 0; }
.small-button { padding: .55rem .7rem; font-size: .82rem; white-space: nowrap; }
.history { margin-top: 3rem; }
.history-message { margin: 0 0 .9rem; color: #536575; }
.secondary-button, .delete-button { padding: .48rem .65rem; font-size: .8rem; white-space: nowrap; }
.secondary-button { border: 1px solid #176a77; background: #fff; color: #176a77; }
.secondary-button:hover { background: #e7f2f3; }
.delete-button { margin-left: .45rem; background: #9d3c36; }
.delete-button:hover { background: #7e2d28; }
.action-cell { min-width: 156px; }
.status { display: inline-block; padding: .2rem .5rem; border-radius: 100px; font-size: .77rem; font-weight: 750; text-transform: capitalize; }
.status.confirmed { color: #135d47; background: #dff5ea; }
.status.cancelled { color: #813630; background: #fde6e3; }
@media (max-width: 620px) { .page-shell { padding: 1rem 0 3rem; } .hero { border-radius: 0 0 20px 20px; } .search-row, .zip-heading { flex-direction: column; align-items: stretch; } .booking-panel { grid-template-columns: 1fr; } .results-heading { display: block; } .results-heading p { margin-top: .45rem; } .results-heading .secondary-button { margin-top: .7rem; } }

</style>
