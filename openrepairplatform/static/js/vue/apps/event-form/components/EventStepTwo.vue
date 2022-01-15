<template>
    <section class="section mt-4">
      <form class="mb-4" @submit.prevent="onSubmit">
        <section class="mb-4">
          <p><b>Quel est l'activité de l'événement ?</b></p>
          <VueMultiselect v-model="activity" :options="optionActivities" label="name" track-by="name"/>
          <div class="invalid-feedback" v-if="error.activities">
            {{ error.activities }}
          </div>
          <section v-if="activity" class="mt-4">
            <div class="card">
              <h5 class="card-header">{{ activity.name }}</h5>
              <div class="card-body">
                <div class="d-flex">
                  <img :src="`/media/${activity.picture}`" v-if="activity.picture" :alt="activity.name" width="200"/>
                  <p class="card-text ms-2" v-html="activity.description"></p>
                </div>
              </div>
            </div>
          </section>
        </section>
        <section class="mb-4" v-if="activity">
          <p><b>
            Si vous souhaitez une description différente de celle proposée par l'ativité sélectionnée, veuillez remplir ce champ.
          </b></p>
          <QuillEditor v-model:content="description" theme="snow" placeholder="Description de l'événement ..."/>
        </section>
        <section class="mb-4" v-if="activity">
          <p><b>Quel est le lieu ?</b></p>
          <VueMultiselect v-model="place" :options="optionPlaces" label="name" track-by="name"/>
          <div class="invalid-feedback" v-if="error.places">
            {{ error.places }}
          </div>
          <section v-if="place" class="mt-4">
            <div class="card">
              <h5 class="card-header">{{ activity.name }}</h5>
              <div class="card-body">
                <div class="d-flex">
                  <img :src="`/media/${place.picture}`" v-if="place.picture" :alt="place.name" width="200"/>
                  <p class="card-text ms-2" v-html="place.description"></p>
                </div>
              </div>
            </div>
          </section>
        </section>
        <section class="mb-4" v-if="place">
          <div class="card text-dark bg-warning mb-3">
            <div class="card-body">
              <div class="form-check">
                <input class="form-check-input" type="checkbox" v-model="allow_stuffs">
                <label class="form-check-label">
                  <b>
                    Nous proposons le recensement des appareils électroniques sur la plateforme
                    afin d'avoir un meilleur suivit et nous permettre d'accumuler des informations
                    sur les pannes récurrentes de certains appareil. Si vous cohez cette case,
                    vous vous engagez à bien noter chaque appareil amené durant l'atelier.
                  </b>
                </label>
              </div>
            </div>
          </div>
        </section>
        <div>
          <button type="button" class="btn btn-primary btn-sm me-2" @click="$emit('previous')">Précedent</button>
          <button type="submit" class="btn btn-primary btn-sm">Suivant</button>
        </div>
      </form>
    </section>
</template>

<script>
import VueMultiselect from 'vue-multiselect'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css';

export default {
  name: 'EventStepTwo',
  components: {
    VueMultiselect,
    QuillEditor,
  },
  props: {
    activities: Array,
    places: Array,
    initials: Object,
  },
  mounted () {
    this.makeOptions(this.activities, this.optionActivities)
    this.makeOptions(this.places, this.optionPlaces)
    this.activity = this.optionActivities.find(
      option => option.pk === this.initials.activity
    )
    this.place = this.optionPlaces.find(
      option => option.pk === this.initials.place
    )
    this.description = this.initials.description
    this.allow_stuffs = this.initials.allow_stuffs
  },
  data () {
    return {
      activity: null,
      place: null,
      description: "",
      allow_stuffs: false,
      optionActivities: [],
      optionPlaces: [],
      error: {
        activities: "",
        places: "",
      }
    }
  },
  methods: {
    onSubmit () {
      if (!this.place || !this.activity) {
        this.error.activities = this.activity ? "" : "Vous devez renseigner une activité."
        this.error.places = this.place ? "" : "Vous devez renseigner un lieu."
      } else {
        this.error.activities = ""
        this.error.places = ""
        this.$emit(
          "next", {
            place: this.place.pk,
            activity: this.activity.pk,
            description: this.description,
            allow_stuffs: this.allow_stuffs
          }
        )
      }
    },
    makeOptions (values, options) {
      values.forEach((value) => {
        options.push({
          name: value.fields.name,
          description: value.fields.description,
          picture: value.fields.picture,
          pk: value.pk,
        })
      })
    }
  }
}
</script>
