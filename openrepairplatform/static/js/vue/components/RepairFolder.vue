<template>

Vous allez créer un dossier de réparation pour cet appareil. 
  <form class="form form-group">
    <label>En cours ?</label>
    <input type="checkbox" v-model="folder.on_going">
    <label>Date d'ouverture</label>
    <input v-model="folder.open_date" type="date" />
    <input v-model="folder.stuff" type="number">
    <button class="btn btn-success" type="submit">Créer</button>
  </form>

<div class="card mb-2" v-for="folder in folders" :key='folder.id'>
    <div class="card-header" data-toggle="collapse" v-bind:href="'#collapse'+folder.id" role="button" aria-expanded="false" :aria-controls="folder.id">
        ouvert le {{ folder.open_date }}
        <span class="float-right">
        <span v-if="folder.ongoing" class="badge badge-pill badge-secondary">En cours</span>
        <span v-if="!folder.ongoing" class="badge badge-pill badge-success">Terminé</span>
        </span><br>
        <small>{{ folder.stuff }}</small><br>
       
    </div>
    <div class="card-body p-0 table-responsive collapse" :id="'collapse' + folder.id">
        <form class="form form-group" v-on:submit.prevent="createIntervention()">
            <input v-model="intervention.observation" type="number">
            <input v-model="intervention.folder" type="number">
            <button class="btn btn-success" type="submit">Créer</button>
        </form>
        <table class="table">
        <thead>
            <tr>
            <th scope="col">Date</th>
            <th scope="col">Observation</th>
            <th scope="col">Raisonement</th>
            <th scope="col">Action</th>
            <th scope="col">Status</th>
            </tr>
        </thead>
        <tbody>
        <tr v-if="folder.interventions" v-for="intervention in folder.interventions.slice().reverse()" :key='intervention.id'>
            <td>
                <small v-if="intervention.event">
                    <a>{{ intervention.event }}</a>
                </small>
                <span v-if="!intervention.event">
                {{ intervention.repair_date }}
                </span>
            </td>
            <td>
                <span v-if="intervention.observation">
                    {{ intervention.observation }}
                </span>
            </td>
            <td>
                <span v-if="intervention.reasoning">
                    {{ intervention.reasoning }}
                </span>
            </td>
            <td>
                <span v-if="intervention.action">
                    {{ intervention.action }}
                </span>
            </td>
            <td>
                <span v-if="intervention.status">
                    {{ intervention.status }}
                </span>
            </td>
        </tr>
        </tbody>
        </table>
    </div>
</div>
</template>

<script>

export default {
  name: 'repairfolder',
  components: {
  },
  data () {
    return {
      folders: [],
      folder: {},
      intervention: {},
    }
  },
  methods: {
    createIntervention: function () {
      fetch('/api/inventory/intervention/', {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFTOKEN': csrftoken
        },
        body: JSON.stringify(this.intervention)
      })
        .then(response => {
          return response.json()
        })
    }
  },
  created () {
    this.stuff_pk = window.localStorage.getItem('stuff_pk');  
    fetch('/api/inventory/stuff/'+this.stuff_pk+'/folder')
      .then(response => {
        return response.json()
      })
      .then(data => {
        this.folders = data
      })
  },
  mounted () {}
}
</script>
