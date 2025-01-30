<template>
    <section class="section">
      <div class="alert alert-success fade show" role="alert" v-if="successMessage">
        {{ successMessage }}
      </div>
      <ul class="nav justify-content-center nav-pills">
        <li class="nav-item">
          <a class="nav-link" :class="{'active': currentStep === 1}" @click="changeStep(1)">
            <span class="badge bg-primary">1</span> Quand
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{'active': currentStep === 2, 'disabled': !validatedSteps.includes(1)}" @click="changeStep(2)">
            <span class="badge bg-primary">2</span> Où et Quoi
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{'active': currentStep === 3, 'disabled': !validatedSteps.includes(2)}" @click="changeStep(3)">
            <span class="badge bg-primary">3</span> Conditions
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{'active': currentStep === 4, 'disabled': !validatedSteps.includes(3)}" @click="changeStep(4)">
            <span class="badge bg-primary">4</span> Récapitulatif
          </a>
        </li>
      </ul>
      <section>
        <EventStepOne @next="getDataOne" v-if="currentStep === 1" :initials="dataOne"/>
        <EventStepTwo @next="getDataTwo" @previous="previousStep" v-if="currentStep === 2" :initials="dataTwo" :activities="activities" :locations="locations"/>
        <EventStepThree @next="getDataThree" @previous="previousStep" v-if="currentStep === 3" :initials="dataThree" :orgaConditions="conditions" :orgaOrganizers="organizers"/>
        <EventStepFour @previous="previousStep" v-if="currentStep === 4" :dataOne="dataOne" :dataTwo="dataTwo" :dataThree="dataThree" :activities="activities" :locations="locations" :conditions="conditions" :organizers="organizers" @submit="submit"/>
      </section>
    </section>
</template>

<script>
import EventStepOne from './components/EventStepOne.vue'
import EventStepTwo from './components/EventStepTwo.vue'
import EventStepThree from './components/EventStepThree.vue'
import EventStepFour from './components/EventStepFour.vue'

import { getNow, post, put } from "../../utils.js"

export default {
  name: 'EventFormApp',
  components: { EventStepOne, EventStepTwo, EventStepThree, EventStepFour },
  data () {
    return {
      dataOne: {
        updated: false,
        recurrent: "",
        date: getNow(),
        publish_at: "",
        recurrent_type: "",
        weeks: [],
        days: [],
        end_date: "",
        period_before_publish: "",
        starts_at: "",
        ends_at: "",
      },
      dataTwo: {
        collaborator: "",
        location: null,
        activity: null,
        description: "",
        allow_stuffs: false,
      },
      dataThree: {
        is_free: true,
        available_seats: 0,
        external: false,
        external_url: "",
        members_only: false,
        conditions: [],
        needed_organizers: 0,
        organizers: [],
      },
      event: null,
      currentStep: 0,
      validatedSteps: [],
      activities: [],
      locations: [],
      conditions: [],
      organizers: [],
      successMessage: "",
    }
  },
  mounted () {
    const target = this.$el.parentElement
    let event = null
    if (target.dataset.event) {
      event = JSON.parse(target.dataset.event)[0]
    } else {
      this.organization = JSON.parse(target.dataset.organization)[0]
    }
    const activities = JSON.parse(target.dataset.activities)
    const locations = JSON.parse(target.dataset.locations)
    const conditions = JSON.parse(target.dataset.conditions)
    const organizers = JSON.parse(target.dataset.organizers)
    if (event) {
      this.dataOne.updated = true
      this.dataOne.recurrent = "non"
      // Data One
      this.dataOne.date = event.fields.date
      this.dataOne.publish_at = event.fields.publish_at.split("Z")[0]
      this.dataOne.starts_at = event.fields.starts_at
      this.dataOne.ends_at = event.fields.ends_at
      // Data two
      this.dataTwo.collaborator = event.fields.collaborator
      this.dataTwo.activity = event.fields.activity
      this.dataTwo.location = event.fields.location
      this.dataTwo.description = event.fields.description
      this.dataTwo.allow_stuffs = event.fields.allow_stuffs
      // Data three
      this.dataThree.is_free = event.fields.is_free
      this.dataThree.available_seats = event.fields.available_seats
      this.dataThree.booking = event.fields.booking
      this.dataThree.external = event.fields.external
      this.dataThree.external_url = event.fields.external_url
      this.dataThree.members_only = event.fields.members_only
      this.dataThree.conditions = event.fields.conditions
      this.dataThree.needed_organizers = event.fields.needed_organizers
      this.dataThree.organizers = event.fields.organizers
      // Validated all steps
      this.validatedSteps = [1, 2, 3]
      this.event = event
    }

    this.activities = activities
    this.locations = locations
    this.conditions = conditions
    this.organizers = organizers

    this.currentStep = 1
  },
  methods: {
    getDataOne (data) {
      this.dataOne = data
      this.validatedSteps.push(1)
      this.nextStep()
    },
    getDataTwo (data) {
      this.dataTwo = data
      this.validatedSteps.push(2)
      this.nextStep()
    },
    getDataThree (data) {
      this.dataThree = data
      this.validatedSteps.push(3)
      this.nextStep()
    },
    nextStep () {
      this.currentStep += 1
    },
    previousStep () {
      this.currentStep -= 1
    },
    changeStep (step) {
      this.currentStep = step
    },
    submit () {
      const data = {...this.dataOne, ...this.dataTwo, ...this.dataThree}
      delete data.recurrent
      delete data.updated
      const url = this.event ? `/api/event/${this.event.pk}/` : "/api/event/"
      if (this.event) {
        data["organization"] = this.event.fields.organization
        put(url, data).then(res => {
          window.location = `/event/${this.event.pk}/${this.event.fields.slug}/admin/`
        }).catch(error => {
          console.log(error)
        })
      } else {
        data["organization"] = this.organization.pk
        post(url, data).then(res => {
          window.location = `/${this.organization.fields.slug}/events/`
        }).catch(error => {
          console.log(error)
        })
      }
    }
  }
}
</script>

<style lang="sass">
.nav-item
  cursor: pointer
</style>
