import { createApp } from 'vue'

import Inventory from './components/Inventory.vue'
import Intervention from './components/Intervention.vue'
import Stuff from './components/Stuff.vue'
import Locationautocomplete from './components/Locationautocomplete.vue'
import RepairFolder from './components/RepairFolder.vue'
import addRepairFolder from './components/addRepairFolder.vue'

import '../../sass/style.sass'
// Initialisation of the application

const vueApps = [
  { id: 'inventory', component: Inventory },
  { id: 'intervention', component: Intervention },
  { id: 'stuff', component: Stuff },
  { id: 'repairfolder', component: RepairFolder },
  { id: 'addrepairfolder', component: addRepairFolder },
  { id: 'locationautocomplete', component: Locationautocomplete },
]

vueApps.forEach(app => {
  if (document.getElementById(app.id)) {
    createApp(app.component).mount(`#${app.id}`)
  }
})
