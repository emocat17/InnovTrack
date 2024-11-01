<template>
  <div>
    <h1>文档收集</h1>
    <button @click="fetchData">获取 TIOBE 排名前10编程语言</button>
    <div v-if="content">
      <h3>爬虫结果：</h3>
      <pre>{{ content }}</pre>
    </div>
  </div>
</template>

<script>
import api from '@/api'

export default {
  data() {
    return {
      content: null,
    }
  },
  methods: {
    async fetchData() {
      try {
        const response = await api.fetchDocumentData()
        this.content = response.data
      } catch (error) {
        console.error('获取数据失败', error)
      }
    },
  },
}
</script>
