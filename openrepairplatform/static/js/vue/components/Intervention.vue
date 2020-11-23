<template>
</template>

<script>

export default {
  name: 'intervention',
  components: {
  },
  data () {
    return {
      stuff: {},
    }
  },
  methods: {
  },
  created () {
    fetch('/api/inventory/stuff/14')
      .then(response => {
        return response.json()
      })
      .then(data => {
        this.stuff = data
      })
  },
  mounted () {}
}
</script>
