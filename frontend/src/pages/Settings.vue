<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'
const s = ref({})
const method = ref('equal_payment')
const saved = ref(false)
onMounted(async () => { s.value = await getJSON('/api/settings'); if (s.value.method) method.value = s.value.method })
const save = async () => { s.value = await putJSON('/api/settings', { method: method.value }); saved.value = true }
</script>
<template><div class="page"><h1>设置</h1>
<label>系统默认还款方式 <select v-model="method">
  <option value="equal_payment">等额本息</option>
  <option value="equal_principal">等额本金</option>
</select></label>
<button @click="save">保存</button>
<span v-if="saved">已保存</span>
<pre>{{ s }}</pre>
</div></template>
