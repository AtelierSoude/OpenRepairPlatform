<template>
    <section class="section mt-4">
      <form class="mb-4" @submit.prevent="onSubmit">
        <div class="input-group mb-3" v-if="!updated">
          <div class="input-group-prepend">
            <label class="input-group-text">
              Est-ce un événement réccurent ?
            </label>
          </div>
          <select required class="custom-select" v-model="recurrent">
            <option value="">Choisir..</option>
            <option value="oui">Oui</option>
            <option value="non">Non</option>
          </select>
        </div>
        <RecurrentComponent v-if="recurrent == 'oui'" @get="getRecurrentData" :error="recurrentError" :initials="recurrentData"/>
        <div v-if="recurrent == 'non'" class="mb-4">
          <div>
            <label>Date de l'événement</label>
            <input required type="date" class="form-control" v-model="data.date" :min="data.date"/>
          </div>
          <div>
            <label>Date de publication</label>
            <input required type="datetime-local" class="form-control" v-model="data.publish_at" :max="`${data.date}T23:59`"/>
          </div>
        </div>
        <div v-if="recurrent !== ''" class="mb-4">
          <div>
            <label>Heure de début</label>
            <input required type="time" class="form-control" v-model="common.starts_at"/>
          </div>
          <div>
            <label>Heure de fin</label>
            <input required type="time" class="form-control" v-model="common.ends_at"/>
          </div>
        </div>
        <div>
          <button type="submit" class="btn btn-primary btn-sm">Suivant</button>
        </div>
      </form>
    </section>
</template>

<script>
import RecurrentComponent from '../../../components/RecurrentComponent.vue'
import { getNow } from "../../../utils.js"

export default {
  name: 'EventStepOne',
  components: { RecurrentComponent },
  props: {
    initials: Object,
  },
  data () {
    return {
      updated: false,
      recurrent: "",
      data: {
        date: getNow(),
        publish_at: "",
      },
      recurrentData: {
        recurrent_type: "",
        weeks: [],
        days: [],
        date: getNow(),
        end_date: "",
        period_before_publish: "",
      },
      common: {
        starts_at: "",
        ends_at: "",
      },
      recurrentError: {
        weeks: "",
        days: "",
      }
    }
  },
  mounted () {
    this.updated = this.initials.updated
    this.recurrent = this.initials.recurrent
    if (this.recurrent === 'oui') {
      this.recurrentData.recurrent_type = this.initials.recurrent_type
      this.recurrentData.weeks = this.initials.weeks
      this.recurrentData.days = this.initials.days
      this.recurrentData.date = this.initials.date
      this.recurrentData.end_date = this.initials.end_date
      this.recurrentData.period_before_publish = this.initials.period_before_publish
    } else if (this.recurrent === 'non') {
      this.data.date = this.initials.date
      this.data.publish_at = this.initials.publish_at
    }
    this.common.starts_at = this.initials.starts_at
    this.common.ends_at = this.initials.ends_at
  },
  methods: {
    onSubmit () {
      if (this.recurrent === "oui") {
        this.checkRecurrentData()
        if (!this.recurrentError.days && !this.recurrentError.weeks) {
          this.$emit("next", {...this.recurrentData, ...this.common, ...{updated: this.updated, recurrent: "oui"}})
        }
      } else if (this.recurrent === "non") {
          this.$emit("next", {...this.data, ...this.common, ...{updated: this.updated, recurrent: "non"}})
      }
    },
    checkRecurrentData () {
      // Check weeks
      if (this.recurrentData.weeks.length === 0 && this.recurrentData.recurrent_type === "MONTHLY") {
        this.recurrentError.weeks = "Vous devez selectionner au moins une semaine."
      } else {
        this.recurrentError.weeks = ""
      }
      // Check days
      if (this.recurrentData.days.length === 0) {
        this.recurrentError.days = "Vous devez selectionner au moins un jour."
      } else {
        this.recurrentError.days = ""
      }
    },
    getRecurrentData (data) {
      this.recurrentData = data
    }
  }

}
</script>

<style lang="sass">
  .input-group-prepend
    flex: 1
  .invalid-feedback
    display: block
</style>
