<template>
  <div class="centered-container">
    <h1 class="title">论文下载</h1>
    <div class="input-container">
      <n-input v-model:value="keyword" placeholder="输入关键字" class="keyword-input" />
      <n-button type="primary" class="download-button" @click="fetchData">下载论文</n-button>
    </div>
    <div v-if="message" class="message">{{ message }}</div>
  </div>
</template>

<script>
import { NButton, NInput, useMessage } from 'naive-ui'
import api from '@/api'

export default {
  components: {
    NButton,
    NInput,
  },
  data() {
    return {
      keyword: '',
      message: '',
    }
  },
  setup() {
    const messageApi = useMessage() // Naive UI 提供的消息提示 API
    return { messageApi }
  },
  methods: {
    async fetchData() {
      if (!this.keyword.trim()) { // 检测输入是否为空
        this.messageApi.warning("请输入一个有效的关键字！") // 显示警告消息
        return
      }
      
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

<style scoped>
.centered-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 70vh;
}

.title {
  font-size: 40px;
  margin-bottom: 20px;
}

.input-container {
  display: flex;
  align-items: center;
}

.keyword-input {
  width: 600px;   /* 输入框宽度 */
  padding: 8px;    /* 输入框的内边距 */
  font-size: 20px;    /* 输入框字体 */
  margin-right: 15px; /* 输入框和按钮间距 */
}

.download-button {
  padding: 23px 30px; /* 按钮的内边距 */
  font-size: 18px; /* 按钮字体 */
}

.message {
  margin-top: 30px;
  font-size: 27px;
}
</style>
