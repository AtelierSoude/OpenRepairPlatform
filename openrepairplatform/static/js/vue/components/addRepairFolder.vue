<template>
Vous allez créer un dossier de réparation pour cet appareil. 
  <form class="form form-group" v-on:submit.prevent="createFolder()">
    <label>En cours ?</label>
    <input type="checkbox" v-model="folder.on_going">
    <label>Date d'ouverture</label>
    <input v-model="folder.open_date" type="date" />
    <input v-model="folder.stuff" type="number">
    <button class="btn btn-success" type="submit">Créer</button>
  </form>
</template>

<script>

export default {
  name: 'addrepairfolder',
  components: {
  },
  data () {
    return {
      folder: {} ,
      folders: [],
    }
  },
  methods: {
    createFolder: function () {
      fetch('/api/inventory/stuff/'+this.stuff_pk+'/folder/', {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFTOKEN': csrftoken
        },
        body: JSON.stringify(this.folder)
      })
        .then(response => {
          return response.json()
        })
    }
  },
  created () {
    this.stuff_pk = window.localStorage.getItem('stuff_pk');  
  },
  mounted () {
  }
}
</script>