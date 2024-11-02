<!-- test -->

<template>
  <div>
    <el-input
      v-model="keyword"
      placeholder="请输入搜索关键字"
      style="width: 300px; margin-right: 10px;"
    ></el-input>
    <button type="primary" @click="handleDownloadPapers">下载论文</button>
    <p v-if="downloadStatus">{{ downloadStatus }}</p>
  </div>
</template>

<script>
import api from '@/api'

export default {
  data() {
    return {
      keyword: '',
      downloadStatus: ''
    };
  },
  methods: {
    async handleDownloadPapers() {
      try {
        const response = await api.downloadPapers(this.keyword);
        this.downloadStatus = response.message;
        // 这里可以处理文件下载，例如使用a标签或者window.open
        window.open(response.file_path);
      } catch (error) {
        this.downloadStatus = '下载失败，请重试。';
        console.error('下载错误', error);
      }
    }
  }
};
</script>
