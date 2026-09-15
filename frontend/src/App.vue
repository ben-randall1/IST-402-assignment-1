<script setup>
import { onMounted, ref } from 'vue'

const apiUrl = 'http://localhost:8000/api'
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
  <main class="page-shell">
    <section class="hero" aria-labelledby="page-title">
      <p class="eyebrow">Travel planning, made simple</p>
      <h1 id="page-title">Find and book your next hotel stay</h1>
      <p class="intro">Search available stays, make a simulated booking, and review your travel history.</p>

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
  </main>
</template>
