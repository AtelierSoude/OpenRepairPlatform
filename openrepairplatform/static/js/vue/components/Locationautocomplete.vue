<template>
<v-select v-model="locations" />
</template>

<script>

export default {  
  name: 'Locationautocomplete',
  components: {},
  data () {
    return {
      locations: []
    }
  },
  methods: {},
  created () {
    fetch('/api/location/place-list/')
      .then(response => {
        console.log(response)
        return response.json()
      })
      .then(data => {
        console.log(data)
        this.locations = data 
      })
  },
  mounted () {}
}
</script>
