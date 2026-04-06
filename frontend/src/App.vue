<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const query = ref('')
const response = ref('')
const intent = ref('')

const ask = async () => {
  try {
    const res = await axios.post('http://localhost:8000/ask', { query: query.value })
    intent.value = res.data.intent
    response.value = res.data.response
  } catch (error) {
    response.value = 'Error: ' + error.message
  }
}
</script>

<template>
  <div>
    <h1>AI 智能问答助手</h1>
    <input v-model="query" placeholder="输入你的查询" />
    <button @click="ask">问答</button>
    <div v-if="intent">
      <p><strong>意图:</strong> {{ intent }}</p>
      <p><strong>响应:</strong> {{ response }}</p>
    </div>
  </div>
</template>

<style scoped>
div {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}
input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
}
button {
  padding: 10px 20px;
}
</style>
