<template>
  <div class="text-center">
    <h1>{{ title }}</h1>
    <div v-for="stuff in stuffs" :key='stuff.id'>
      <div v-if="stuff.device">{{stuff.device.name}}</div>
      <input v-if="stuff.device" v-model="stuff.device">
    </div>
  </div>
</template>

<script>

export default {
  name: 'Inventory',
  components: {},
  data () {
    return {
      title: 'Inventaire',
      stuffs: [],
      stuff: {}
    }
  },
  methods: {},
  created () {
    fetch('/api/inventory/stuff/')
      .then(response => {
        console.log(response)
        return response.json()
      })
      .then(data => {
        console.log(data)
        this.stuffs = data
      })
  },
  mounted () {}
}
</script>
