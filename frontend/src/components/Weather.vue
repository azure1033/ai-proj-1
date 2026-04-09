<template>
  <section class="card weather-card">
    <div class="card-header">
      <div>
        <h2>天气查询</h2>
        <p>输入城市名称，获取当前天气和生活建议。</p>
      </div>
      <span class="status-chip" :class="{ loading: isLoading }">
        {{ isLoading ? '查询中...' : '准备就绪' }}
      </span>
    </div>

    <div class="weather-input">
      <input
        v-model="city"
        type="text"
        placeholder="例如：北京、上海、New York"
        @keyup.enter="getWeather"
      />
      <button class="action-btn" @click="getWeather" :disabled="isLoading || !city.trim()">
        {{ isLoading ? '查询中...' : '获取天气' }}
      </button>
    </div>

    <div class="weather-result" v-if="weatherResponse">
      <pre>{{ weatherResponse }}</pre>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const city = ref('')
const weatherResponse = ref('')
const isLoading = ref(false)

const getWeather = async () => {
  if (!city.value.trim()) {
    weatherResponse.value = '请输入城市名称。'
    return
  }

  isLoading.value = true
  weatherResponse.value = ''

  try {
    const res = await axios.post('http://localhost:8000/weather', { city: city.value })
    weatherResponse.value = res.data.response
  } catch (error: any) {
    weatherResponse.value = error?.response?.data?.detail || error.message || '查询失败，请稍后重试。'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.weather-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
  backdrop-filter: blur(10px);
}

.weather-input {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.weather-input input {
  flex: 1;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #ffffff;
  font-size: 14px;
}

.weather-input input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.weather-result {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 16px;
}

.weather-result pre {
  white-space: pre-wrap;
  color: #ffffff;
  font-family: inherit;
  margin: 0;
}
</style>