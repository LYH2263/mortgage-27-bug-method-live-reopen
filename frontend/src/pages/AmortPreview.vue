<script setup>
import { onMounted, ref, watch } from 'vue'
import { getJSON, postJSON } from '../api'
const method = ref('equal_payment')
const out = ref(null)
const load = async () => { out.value = await postJSON('/api/schedule', { principal: 1000000, annual_rate: 3.5, months: 360, method: method.value, persist: false, preview_rows: 12 }) }
watch(method, load, { immediate: true })
onMounted(async () => {
  const s = await getJSON('/api/settings')
  if (s.method && s.method !== method.value) method.value = s.method
})
</script>
<template><div class="page"><h1>摊还表预览</h1>
<label>还款方式 <select v-model="method">
  <option value="equal_payment">等额本息</option>
  <option value="equal_principal">等额本金</option>
</select></label>
<template v-if="out">
  <p v-if="out.method === 'equal_principal'">首期月供 {{ out.first_payment }} · 末期月供 {{ out.last_payment }} · 利息合计 {{ out.total_interest }} · 还款合计 {{ out.total_payment }}</p>
  <p v-else>月供 {{ out.monthly_payment }} · 利息合计 {{ out.total_interest }} · 还款合计 {{ out.total_payment }}</p>
  <table><tr><th>期次</th><th>月供</th><th>本金</th><th>利息</th><th>余额</th></tr>
  <tr v-for="r in out.preview" :key="r.period"><td>第{{ r.period }}期</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td></tr></table>
</template>
</div></template>
