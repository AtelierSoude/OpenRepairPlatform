import { createApp } from 'vue'
import Inventory from './components/Inventory.vue'
import Intervention from './components/Intervention.vue'

import '../../sass/style.sass'

// Initialisation of the application
const vueApps = [
  { id: 'inventory', component: Inventory },
  { id: 'intervention', component: Intervention }
]

vueApps.forEach(app => {
  if (document.getElementById(app.id)) {
    createApp(app.component).mount(`#${app.id}`)
  }
})
