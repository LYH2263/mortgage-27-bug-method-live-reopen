<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'
const route = useRoute()
const loan = ref(null)
const sch = ref(null)
const method = ref('equal_payment')
const load = async () => {
  loan.value = await getJSON(`/api/loans/${route.params.id}`)
  sch.value = await postJSON('/api/schedule', { principal: loan.value.principal, annual_rate: loan.value.annual_rate, months: loan.value.months, method: method.value, loan_id: loan.value.id, persist: false, preview_rows: 6 })
}
onMounted(load); watch(() => route.params.id, load); watch(method, load)
</script>
<template><div class="page" v-if="loan"><h1>{{ loan.name }}</h1>
<label>还款方式 <select v-model="method">
  <option value="equal_payment">等额本息</option>
  <option value="equal_principal">等额本金</option>
</select></label>
<p v-if="sch?.method === 'equal_principal'">首期月供 <span class="hero-num">{{ sch?.first_payment }}</span> · 末期月供 {{ sch?.last_payment }}</p>
<p v-else>月供 <span class="hero-num">{{ sch?.monthly_payment }}</span></p>
<table><tr v-for="r in sch?.preview" :key="r.period"><td>{{ r.period }}</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td></tr></table>
</div></template>
