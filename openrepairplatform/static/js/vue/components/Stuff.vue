<template>
<form v-on:submit.prevent="updateStuff()">
    <h4 class="pt-2 pb-2 header_detail_page_title">Titre
    </h4>
    <div class="card col-md-12 mb-2 p-3">
        <span>
        <b class="pr-2">Categorie</b> 
        <span v-show="!stuff.edit">{{stuff.category_name}} > {{stuff.device_name}}</span> 
        <input v-model="stuff.device" v-show="stuff.edit">
          <a v-show="!stuff.edit" v-on:click="editStuff(stuff)" class="btn btn-default rounded-circle btn-sm float-right">
            <i class="fa fa-pencil-alt"></i>
        </a>
        <button type="submit" v-show="stuff.edit" v-on:click="confirmStuff(stuff)" class="btn btn-success rounded-circle btn-sm float-right">
            <i class="fas fa-check"></i>
        </button>
        </span>
    </div>
    <div class="card col-md-12 mb-2 p-3">
        <span>
        <b class="pr-2">Propriétaire</b> 
        <span v-show="!stuff.edit">{{stuff.organization_owner_name}}</span>
        <input v-model="stuff.organization_owner" v-show="stuff.edit">
          <a v-show="!stuff.edit" v-on:click="editStuff(stuff)" class="btn btn-default rounded-circle btn-sm float-right">
            <i class="fa fa-pencil-alt"></i>
        </a>
        <button type="submit" v-show="stuff.edit" v-on:click="confirmStuff(stuff)" class="btn btn-success rounded-circle btn-sm float-right">
            <i class="fas fa-check"></i>
        </button>
        </span>
    </div>
    <div class="card col-md-12 mb-2 p-3">
        <span>
        <b class="pr-2">Localisation</b> 
        <span v-show="!stuff.edit">{{stuff.place_name}}</span>
         <input v-model="stuff.place" v-show="stuff.edit">
           <a v-show="!stuff.edit" v-on:click="editStuff(stuff)" class="btn btn-default rounded-circle btn-sm float-right">
            <i class="fa fa-pencil-alt"></i>
        </a>
        <button type="submit" v-show="stuff.edit" v-on:click="confirmStuff(stuff)" class="btn btn-success rounded-circle btn-sm float-right">
            <i class="fas fa-check"></i>
        </button>
    </span>
    </div>
    <div class="card col-md-12 mb-2 p-3">
        <span>
        <b class="pr-2">Etat</b> 
        <span v-show="!stuff.edit">{{stuff.state}}</span>
        <input v-model="stuff.state" v-show="stuff.edit">
        <a v-show="!stuff.edit" v-on:click="editStuff(stuff)" class="btn btn-default rounded-circle btn-sm float-right">
            <i class="fa fa-pencil-alt"></i>
        </a>
        <button type="submit" v-show="stuff.edit" v-on:click="confirmStuff(stuff)" class="btn btn-success rounded-circle btn-sm float-right">
            <i class="fas fa-check"></i>
        </button>
        </span>
    </div>
</form>
</template>

<script>

export default {
  name: 'stuff',
  components: {
  },
  data () {
    return {
      stuff: {},
    }
  },
  methods: {
    editStuff: function (stuff) {
        this._originalStuff = Object.assign({}, stuff);
        stuff.edit = true;
          },
    confirmStuff: function (stuff) {
        this._originalStuff = Object.assign({}, stuff);
        stuff.edit = false;
          },
    updateStuff: function () {
      fetch('/api/inventory/stuff/'+this.stuff_pk+'/', {
        method: 'PUT',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFTOKEN': csrftoken
        },
        body: JSON.stringify(this.stuff)
      })
        .then(response => {
          return response.json()
        })
        .then(data => {
        this.stuff = data
      })
    }
  },
  created () {
    this.stuff_pk = window.localStorage.getItem('stuff_pk');  
    fetch('/api/inventory/stuff/'+this.stuff_pk)
      .then(response => {
        return response.json()
      })
      .then(data => {
        this.stuff = data
      })
  },
  mounted () {
  }
}
</script>
