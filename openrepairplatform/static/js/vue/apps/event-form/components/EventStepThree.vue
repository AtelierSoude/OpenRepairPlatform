<template>
    <section class="section mt-4">
      <form class="mb-4" @submit.prevent="onSubmit">
        <section class="mb-4">
          <div class="form-check mb-4">
            <input class="form-check-input" type="checkbox" v-model="is_free">
            <label class="form-check-label"><b>L'évenement n'a pas de limite de place</b></label>
          </div>
          <div class="mb-4" v-if="!is_free">
            <p>Nombre de places :</p>
            <input type="number" min="0" v-if="!is_free" class="form-control mb-4" placeholder="Nombre de places" v-model="available_seats"/>
          </div>
          <div class="form-check mb-4">
            <input class="form-check-input" type="checkbox" v-model="booking">
            <label class="form-check-label"><b>L'évenement nécessite une réservation</b></label>
          </div>
          <template v-if="booking">
            <div class="form-check mb-4" v-if="booking">
              <input class="form-check-input" type="checkbox" v-model="external">
              <label class="form-check-label"><b>La réservation est externe</b></label>
            </div>
          </template>
          <div class="mb-4">
            <input type="url" v-model="external_url" v-if="external" class="form-control" required placeholder="Ajouter un lien vers la réservation externe."/>
            <input type="url" v-model="external_url" v-else class="form-control" placeholder="Ajouter un lien pour avoir des informations supplémentaires."/>
          </div>
          <div class="form-check mb-4">
            <input class="form-check-input" type="checkbox" v-model="members_only">
            <label class="form-check-label"><b>L'évenement est réservé aux membres</b></label>
          </div>
          <div class="mb-4">
            <p><b>Autres conditions :</b></p>
            <VueMultiselect v-model="conditions" :multiple="true" :options="optionConditions" label="name" track-by="name"/>
          </div>
          <section class="mb-4" v-if="conditions.length > 0">
            <div v-for="condition in conditions" :key="condition.pk" class="card mb-2">
              <h5 class="card-header">{{ condition.name }}</h5>
              <div class="card-body">
                <p class="card-text ms-2" v-html="condition.description"></p>
                <b v-if="condition.price > 0">{{ condition.price }} €</b>
              </div>
            </div>
          </section>

          <div class="mb-4">
            <p><b>Nombre d'animateurs attendus</b></p>
            <input v-model="needed_organizers" class="form-control" type="number" min="0" placeholder="Nombre d'animateur"/>
          </div>

          <div class="mb-2">
            <p><b>Animateurs :</b></p>
            <VueMultiselect v-model="organizers" :multiple="true" :options="optionOrganizers" label="name" track-by="name"/>
          </div>

          <section class="mb-4">
            <p><b>
              Notes internes :
            </b></p>
            <QuillEditor v-model:content="internal_notes" contentType="html" theme="snow" value:="value" placeholder="Note internes pour les animateurs..."/>
          </section>
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

export default {
  name: 'EventStepThree',
  components: {
    VueMultiselect,
    QuillEditor,
  },
  props: {
    initials: Object,
    orgaConditions: Array,
    orgaOrganizers: Array,
  },
  mounted () {
    this.makeOptions(this.orgaConditions, this.optionConditions)
    this.makeOrgaOptions(this.orgaOrganizers, this.optionOrganizers)

    this.initials.conditions.forEach(condition => {
      const c = this.optionConditions.find(c => c.pk === condition)
      this.conditions.push(c)
    })
    this.initials.organizers.forEach(organizer => {
      const o = this.optionOrganizers.find(o => o.pk === organizer)
      this.organizers.push(o)
    })

    this.is_free = this.initials.is_free
    this.available_seats = this.initials.available_seats
    this.booking = this.initials.booking
    this.external = this.initials.external
    this.external_url = this.initials.external_url
    this.members_only = this.initials.members_only
    this.needed_organizers = this.initials.needed_organizers
    this.internal_notes = this.initials.internal_notes
  },
  data () {
    return {
      optionConditions: [],
      optionOrganizers: [],
      is_free: true,
      available_seats: 0,
      booking: false,
      external: false,
      external_url: "",
      members_only: false,
      conditions: [],
      needed_organizers: 0,
      organizers: [],
      internal_notes: "",
    }
  },
  methods: {
    onSubmit () {
      const conditions = []
      this.conditions.forEach(condition => {
        conditions.push(condition.pk)
      })
      const organizers = []
      this.organizers.forEach(organizer => {
        organizers.push(organizer.pk)
      })
      this.$emit(
        "next", {
          is_free: this.is_free,
          available_seats: this.available_seats,
          booking: this.booking,
          external: this.external,
          external_url: this.external_url,
          members_only: this.members_only,
          conditions: conditions,
          needed_organizers: this.needed_organizers,
          organizers: organizers,
          internal_notes: this.internal_notes,
        }
      )
    },
    makeOptions (values, options) {
      values.forEach((value) => {
        options.push({
          name: value.fields.name,
          description: value.fields.description,
          price: value.fields.price,
          pk: value.pk,
        })
      })
    },
    makeOrgaOptions (values, options) {
      values.forEach((value) => {
        options.push({
          name: `${value.fields.first_name} ${value.fields.last_name}`,
          first_name: value.fields.first_name,
          last_name: value.fields.last_name,
          avatar_img: value.fields.avatar_img,
          pk: value.pk,
        })
      })
    }
  },
}
</script>

<style lang="sass">
.organizer-list
  h5
    margin: 0
    padding: 0
    display: flex
    align-items: center
</style>
