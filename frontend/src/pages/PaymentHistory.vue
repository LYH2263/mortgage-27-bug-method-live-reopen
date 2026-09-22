<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const detail = ref(null)
const METHOD_LABEL = { equal_payment: '等额本息', equal_principal: '等额本金' }
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
const open = async (id) => { detail.value = await getJSON(`/api/history/${id}`) }
</script>
<template><div class="page"><h1>试算记录</h1>
<table><tr><th>编号</th><th>时间</th><th>方式</th><th>利息合计</th><th></th></tr>
<tr v-for="h in items" :key="h.id"><td>#{{ h.id }}</td><td>{{ h.created_at }}</td><td>{{ METHOD_LABEL[h.method] || h.method }}</td><td>{{ h.total_interest }}</td><td><button @click="open(h.id)">查看</button></td></tr></table>
<template v-if="detail">
  <h2>#{{ detail.id }} {{ METHOD_LABEL[detail.method] || detail.method }}</h2>
  <p v-if="detail.method === 'equal_principal'">首期月供 {{ detail.result.first_payment }} · 末期月供 {{ detail.result.last_payment }} · 利息合计 {{ detail.total_interest }}</p>
  <p v-else>月供 {{ detail.result.monthly_payment }} · 利息合计 {{ detail.total_interest }}</p>
  <table><tr><th>期次</th><th>月供</th><th>本金</th><th>利息</th><th>余额</th></tr>
  <tr v-for="r in detail.result.preview" :key="r.period"><td>第{{ r.period }}期</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td></tr></table>
</template>
</div></template>
