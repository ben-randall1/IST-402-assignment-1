<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const props = defineProps({ center: Object, hotels: Array, selectedId: String })
const emit = defineEmits(['select'])
const container = ref(null)
const tileError = ref(false)
let map, layer, radius, resizeObserver
const markers = new Map()

function fitArea() {
  if (radius) map.fitBounds(radius.getBounds(), { padding: [25, 25], animate: false })
}

function draw() {
  if (!map || !props.center) return
  layer.clearLayers()
  markers.clear()
  const point = [props.center.latitude, props.center.longitude]
  radius = L.circle(point, { radius: 5000, color: '#547252', weight: 1.5, dashArray: '5 7', fillColor: '#7f9c65', fillOpacity: 0.055 }).addTo(layer)
  L.circleMarker(point, { radius: 6, color: '#fff', weight: 3, fillColor: '#557b97', fillOpacity: 1 })
    .bindTooltip(`ZIP ${props.center.postcode} search center`).addTo(layer)
  props.hotels.forEach((hotel, index) => {
    const title = `Map hotel ${index + 1}: ${hotel.name || 'Name unavailable'}`
    const marker = L.marker([hotel.latitude, hotel.longitude], {
      icon: L.divIcon({ className: 'hotel-pin', html: `<span>${index + 1}</span>`, iconSize: [36, 36], iconAnchor: [18, 18] }),
      keyboard: true, title, alt: title, riseOnHover: true,
    }).addTo(layer)
    const popup = document.createElement('div')
    const name = document.createElement('strong')
    name.textContent = hotel.name || 'Hotel name unavailable'
    const address = document.createElement('p')
    address.textContent = hotel.address || 'Address not supplied'
    popup.append(name, address)
    marker.bindPopup(popup, { closeButton: true, autoPan: true })
    marker.on('click', () => emit('select', hotel.place_id))
    const element = marker.getElement()
    element.setAttribute('aria-label', title)
    element.addEventListener('keydown', event => {
      if (event.key === ' ' || event.key === 'Enter') {
        event.preventDefault()
        event.stopPropagation()
        emit('select', hotel.place_id)
      }
    })
    markers.set(hotel.place_id, marker)
  })
  fitArea()
  updateSelection()
}

function updateSelection() {
  markers.forEach((marker, id) => {
    const selected = id === props.selectedId
    marker.getElement()?.classList.toggle('is-selected', selected)
    marker.getElement()?.setAttribute('aria-pressed', String(selected))
    marker.setZIndexOffset(selected ? 1000 : 0)
    if (selected) {
      map.setView(marker.getLatLng(), Math.max(map.getZoom(), 15), { animate: false })
      marker.openPopup()
    }
  })
}

onMounted(() => {
  map = L.map(container.value, { scrollWheelZoom: false, zoomControl: false, attributionControl: true })
    .setView([props.center.latitude, props.center.longitude], 13)
  L.control.zoom({ position: 'topright' }).addTo(map)
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).on('tileerror', () => { tileError.value = true }).addTo(map)
  layer = L.layerGroup().addTo(map)
  resizeObserver = new ResizeObserver(() => map.invalidateSize())
  resizeObserver.observe(container.value)
  draw()
})
watch(() => props.center, draw)
watch(() => props.selectedId, updateSelection)
onBeforeUnmount(() => { resizeObserver?.disconnect(); map?.remove() })
</script>

<template>
  <section class="map-frame" aria-label="Hotel locations map">
    <div ref="container" class="hotel-map" aria-label="Interactive hotel map. Use Tab to select numbered hotels; Enter or Space activates a marker." />
    <button class="map-fit" type="button" @click="fitArea">↗ Show search area</button>
    <div class="map-legend"><span class="center-dot"></span> ZIP location <span class="radius-swatch"></span> 5 km radius</div>
    <p v-if="tileError" class="tile-warning" role="status">Some map imagery couldn’t load. Hotel markers and the list are still available.</p>
  </section>
</template>
