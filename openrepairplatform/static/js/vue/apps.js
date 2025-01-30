import { createApp } from 'vue'
import EventFormApp from './apps/event-form/EventFormApp.vue'


// Initialisation of the application
const vueApps = [
  { id: 'event-form-app', component: EventFormApp }
]

vueApps.forEach(app => {
  if (document.getElementById(app.id)) {
    const vueApp = createApp(app.component)
    vueApp.mount(`#${app.id}`)
  }
})
