<template>
  <div>
    <input v-model="keyword" placeholder="输入关键字" />
    <button @click="fetchData">下载论文</button>
    <div v-if="message">{{ message }}</div>
  </div>
</template>

<script>
import api from '@/api'

export default {
  data() {
    return {
      keyword: '',
      message: '',
    }
  },

  methods: {
    async fetchData() {
      this.message = `正在下载与"${this.keyword}"相关的论文...`
      try {
        await api.fetchArxivData(this.keyword)
        this.message = `下载完成！`
      } catch (error) {
        console.error('下载失败', error)
        this.message = '下载失败，请重试。'
      }
    },
  },
}
</script>
