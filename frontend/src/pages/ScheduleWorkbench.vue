<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
const principal = ref(800000)
const annual_rate = ref(4.2)
const months = ref(360)
const method = ref('equal_payment')
const out = ref(null)
onMounted(async () => { const s = await getJSON('/api/settings'); if (s.method) method.value = s.method })
const run = async () => { out.value = await postJSON('/api/schedule', { principal: principal.value, annual_rate: annual_rate.value, months: months.value, method: method.value, persist: true }) }
</script>
<template><div class="page"><h1>月供试算</h1>
<label>还款方式 <select v-model="method">
  <option value="equal_payment">等额本息</option>
  <option value="equal_principal">等额本金</option>
</select></label>
<label>本金 <input v-model.number="principal" /></label>
<label>年利率% <input v-model.number="annual_rate" /></label>
<label>月数 <input v-model.number="months" /></label>
<button @click="run">计算</button>
<template v-if="out">
  <p v-if="out.method === 'equal_principal'">首期月供 {{ out.first_payment }} · 末期月供 {{ out.last_payment }} · 利息合计 {{ out.total_interest }}</p>
  <p v-else>月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }}</p>
</template>
</div></template>
