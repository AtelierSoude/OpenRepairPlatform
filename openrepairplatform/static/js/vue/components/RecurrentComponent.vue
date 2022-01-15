<template>
  <div class="mb-4">
    <div class="input-group mb-3">
      <div class="input-group-prepend">
        <label class="input-group-text">
          Par :
        </label>
      </div>
      <select required class="custom-select" v-model="data.recurrent_type" @input="sendRecurentData">
        <option value="">Choisir..</option>
        <option value="MONTHLY">Mois</option>
        <option value="WEEKLY">Semaine</option>
      </select>
    </div>
    <!-- Weeks -->
    <template v-if="data.recurrent_type !== '' && data.recurrent_type == 'MONTHLY'">
      <div class="mb-2">
        <label class="form-label fw-bold">La ou les semaines : </label>
        <div class="d-flex flex-wrap">
          <div class="form-check me-2" v-for="week in weeks" :key="week.value">
            <input class="form-check-input" type="checkbox" :value="week.value" v-model="data.weeks" @input="sendRecurentData">
            <label class="form-check-label">{{ week.label }}</label>
          </div>
          <div class="invalid-feedback" v-if="error.weeks">
            {{ error.weeks }}
          </div>
        </div>
      </div>
    </template>
    <template v-if="data.recurrent_type !== ''">
      <!-- Days -->
      <div class="mb-2">
        <label class="form-label fw-bold">Jour(s) : </label>
        <div class="d-flex flex-wrap">
          <div class="form-check me-2" v-for="day in days" :key="day.value">
            <input class="form-check-input" type="checkbox" :value="day.value" v-model="data.days" @input="sendRecurentData">
            <label class="form-check-label">{{ day.label }}</label>
          </div>
          <div class="invalid-feedback" v-if="error.days">
            {{ error.days }}
          </div>
        </div>
      </div>
      <!-- Date start -->
      <div class="mb-2">
        <label class="form-label fw-bold">Date de début de la récurrence : </label>
        <input required type="date" class="form-control" v-model="data.date" @input="sendRecurentData" :min="data.date"/>
      </div>
      <!-- Date end -->
      <div class="mb-2">
        <label class="form-label fw-bold">Date de fin de la récurrence : </label>
        <input required type="date" class="form-control" v-model="data.end_date" @input="sendRecurentData"/>
      </div>
      <!-- Publication -->
      <div class="mb-2">
        <label class="form-label fw-bold">Publication : </label>
        <select required class="form-select" aria-label="Date de publication à selectionner" v-model="data.period_before_publish" @input="sendRecurentData">
          <option value="">Choisir..</option>
          <option v-for="period in periods" :key="period.value" :value="period.value">
            {{ period.label }}
          </option>
        </select>
      </div>
    </template>
  </div>
</template>

<script>
import { getNow } from "../utils.js"

export default {
  name: "RecurrentComponent",
  props: {
    error: Object,
    initials: Object,
  },
  data () {
    return {
      weeks: [
        {value: 1, label: "Semaine 1"},
        {value: 2, label: "Semaine 2"},
        {value: 3, label: "Semaine 3"},
        {value: 4, label: "Semaine 4"},
        {value: 5, label: "Semaine 5"},
      ],
      days: [
        {value: "MO", label: "Lundi"},
        {value: "TU", label: "Mardi"},
        {value: "WE", label: "Mercredi"},
        {value: "TH", label: "Jeudi"},
        {value: "FR", label: "Vendredi"},
        {value: "SA", label: "Samedi"},
        {value: "SU", label: "Dimanche"},
      ],
      periods: [
        {value: 1, label: "1 jour avant"},
        {value: 2, label: "2 jours avant"},
        {value: 7, label: "Une semaine avant"},
        {value: 14, label: "Deux semaines avant"},
        {value: 21, label: "Trois semaines avant"},
        {value: 28, label: "Quatre semaines avant"},
        {value: 35, label: "Cinq semaines avant"},
        {value: 42, label: "Six semaines avant"},
      ],
      data: {
        recurrent_type: "",
        weeks: [],
        days: [],
        date: getNow(),
        end_date: "",
        period_before_publish: "",
      },
    }
  },
  mounted () {
    this.data = this.initials
  },
  methods: {
    sendRecurentData () {
      this.$emit("get", this.data)
    },
  }
}
</script>

<style lang="sass"></style>
