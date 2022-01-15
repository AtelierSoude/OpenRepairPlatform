<template>
  <section class="section">

    <template v-if="data.recurrent === 'oui'">
      <label>Date de début :</label>
      <input class="form-control" type="date" :value="data.date" disabled/>
      <label>Date de fin :</label>
      <input class="form-control" type="date" :value="data.end_date" disabled/>
      <label>Heure de début :</label>
      <input class="form-control" type="time" :value="data.starts_at" disabled/>
      <label>Heure de fin :</label>
      <input class="form-control" type="time" :value="data.ends_at" disabled/>
      <p class="mt-2"><b>Période avant la publication : {{ data.period_before_publish }} jour(s) avant</b></p>
    </template>

    <template v-else>
      <label>Date :</label>
      <input class="form-control" type="date" :value="data.date" disabled/>
      <label>Date de publication :</label>
      <input class="form-control" type="datetime-local" :value="data.publish_at" disabled/>
      <label>Heure de début :</label>
      <input class="form-control" type="time" :value="data.starts_at" disabled/>
      <label>Heure de fin :</label>
      <input class="form-control" type="time" :value="data.ends_at" disabled/>
    </template>

    <hr/>

    <label>Lieux :</label>
    <section class="mb-4" v-if="data.location">
      <div class="card">
        <h5 class="card-header">{{ data.location.fields.name }}</h5>
        <div class="card-body">
          <p class="card-text ms-2" v-html="data.location.fields.description"></p>
        </div>
      </div>
    </section>

    <label>Activité :</label>
    <section class="mb-4" v-if="data.activity">
      <div class="card">
        <h5 class="card-header">{{ data.activity.fields.name }}</h5>
        <div class="card-body">
          <p class="card-text ms-2" v-html="data.activity.fields.description"></p>
        </div>
      </div>
    </section>

    <template v-if="data.description">
      <label>Description :</label>
      <section class="mb-4">
        <div class="card">
          <div class="card-body">
            <p class="card-text ms-2" v-html="data.description"></p>
          </div>
        </div>
      </section>
    </template>

    <label>L'évenement recense le matériel électronique :</label>
    <p><b v-if="data.allow_stuffs">Oui</b><b v-else>Non</b></p>

    <label>L'évenement n'a pas de limite de place :</label>
    <p><b v-if="data.is_free">Oui</b><b v-else>Non</b></p>

    <p v-if="!data.is_free"><b>Il y a {{ data.available_seats }} places disponibles.</b></p>

    <label>L'évenement nécessite une réservation :</label>
    <p><b v-if="data.booking">Oui</b><b v-else>Non</b></p>

    <template v-if="data.booking">
      <label>La réservation de l'évenement est externe à la plateforme :</label>
      <p><b v-if="data.external">Oui</b><b v-else>Non</b></p>
      <p v-if="data.external">Le lien pour réservé est : <a :href="data.external_url">{{ data.external_url }}</a></p>
      <p v-if="!data.external && data.external_url">
        Le lien pour plus d'information : <a :href="data.external_url">{{ data.external_url }}</a>
      </p>
    </template>

    <label>L'évenement est réservé aux membres :</label>
    <p><b v-if="data.members_only">Oui</b><b v-else>Non</b></p>

    <p><b>L'évenement a besoin de {{ data.needed_organizers }} animateurs.</b></p>

    <template v-if="data.conditions.length">
      <label>Conditions :</label>
      <section class="mb-4">
        <div class="card" v-for="condition in data.conditions" :key="condition.pk">
          <h5 class="card-header">{{ condition.fields.name }}</h5>
          <div class="card-body">
            <p class="card-text ms-2" v-html="condition.fields.description"></p>
            <b v-if="condition.price">{{ condition.fields.price }} €</b>
          </div>
        </div>
      </section>
    </template>

    <template v-if="data.organizers">
      <label>Animateurs :</label>
      <section class="mb-4">
        <div class="card mb-2" v-for="organizer in data.organizers" :key="organizer.pk">
          <p class="card-header">{{ organizer.fields.first_name }} {{ organizer.fields.last_name }}</p>
        </div>
      </section>
    </template>

    <button class="btn btn-success" @click="submitEvent">Enregistrer</button>

  </section>
</template>

<script>
export default {
  name: 'EventStepFour',
  props: {
    dataOne: Object,
    dataTwo: Object,
    dataThree: Object,
    activities: Array,
    locations: Array,
    conditions: Array,
    organizers: Array,
  },
  components: {},
  data () {
    return {
      data: {
        conditions: [],
        organizers: [],
      },
    }
  },
  mounted () {
    this.data = {...this.dataOne, ...this.dataTwo, ...this.dataThree}
    this.data.activity = this.activities.find(activity => activity.pk === this.data.activity)
    this.data.location = this.locations.find(location => location.pk === this.data.location)
    this.data.conditions = this.conditions.filter(condition => this.data.conditions.includes(condition.pk))
    this.data.organizers = this.organizers.filter(organizer => this.data.organizers.includes(organizer.pk))
    console.log(this.data)
  },
  methods: {
    submitEvent () {
      this.$emit('submit')
    }
  },
}
</script>

<style lang="sass"></style>
