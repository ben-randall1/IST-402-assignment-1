<script setup>
import { ref } from 'vue'

const city = ref('Boston')
const stays = ref([])
const message = ref('Search a city to find its available hotel stays.')
const loading = ref(false)
const hasSearched = ref(false)

async function search() {
  const query = city.value.trim()
  if (!query) {
    stays.value = []
    hasSearched.value = false
    message.value = 'Enter a city before searching.'
    return
  }

  loading.value = true
  hasSearched.value = false
  message.value = 'Searching for hotel stays…'
  try {
    const response = await fetch(`http://localhost:8000/api/stays?city=${encodeURIComponent(query)}`)
    if (!response.ok) throw new Error('The server could not complete the search.')
    const result = await response.json()
    stays.value = result.stays
    hasSearched.value = true
    message.value = result.count
      ? `${result.count} stay${result.count === 1 ? '' : 's'} found in ${result.city}.`
      : `No hotel stays match “${result.city}”. Try another city.`
  } catch (error) {
    stays.value = []
    message.value = error.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="page-shell">
    <section class="hero" aria-labelledby="page-title">
      <p class="eyebrow">Travel planning, made simple</p>
      <h1 id="page-title">Find your next hotel stay</h1>
      <p class="intro">Search our available trips by city.</p>

      <form class="search-panel" @submit.prevent="search">
        <label for="city">City</label>
        <div class="search-row">
          <input id="city" v-model="city" name="city" placeholder="e.g., Boston" autocomplete="address-level2" />
          <button type="submit" :disabled="loading">{{ loading ? 'Searching…' : 'Search' }}</button>
        </div>
      </form>
    </section>

    <section class="results" aria-live="polite" aria-labelledby="results-title">
      <div class="results-heading">
        <h2 id="results-title">Matching hotel stays</h2>
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
              <th scope="col">Nightly rate</th>
              <th scope="col">Stay price</th>
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
              <td>{{ stay.nightly_rate }}</td>
              <td>{{ stay.stay_price }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>
