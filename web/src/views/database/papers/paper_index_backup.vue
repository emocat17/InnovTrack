<script setup>
import { onMounted, ref } from 'vue'
import { NInput, NButton, NDataTable } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import api from '@/api'

defineOptions({ name: '论文数据库' })

// 表格和消息状态的响应式变量
const data = ref([])  // 存储表格数据
const message = ref('')  // 显示加载状态或错误信息
const queryItems = ref({ keyword: 'zero trust' })  // 用于存储查询关键字

// 表格的列配置
const columns = [
  { title: '发布日期', key: '发布日期', align: 'center', width: 120, ellipsis: { tooltip: true }},
  { title: '标题', key: '标题', align: 'center'},
  { title: '作者', key: '作者', align: 'center'}, //, ellipsis: { tooltip: true } :使数据不会被截断;摘要太长了加上截断
  { title: '摘要', key: '摘要', align: 'center', width: 200, ellipsis: { tooltip: true }},
  // { title: '链接', key: '链接', align: 'center', ellipsis: { tooltip: true }},
  // { title: 'PDF链接', key: 'PDF链接', align: 'center', ellipsis: { tooltip: true }},
  { title: '链接', key: '链接', align: 'center', width: 120, ellipsis: { tooltip: true }, 
    render(row) {
      return h(NButton, { size: "small", onClick: () => openLink(row['链接']) }, { default: () => '访问链接' })
    }
  },
  { title: 'PDF链接', key: 'PDF链接', align: 'center', width: 120, ellipsis: { tooltip: true }, 
    render(row) {
      return h(NButton, { size: "small", onClick: () => openLink(row['PDF链接']) }, { default: () => '下载PDF' })
    }
  },
]

// 获取数据函数
const fetchData = async () => {
  message.value = `正在加载与 "${queryItems.value.keyword}" 相关的数据...`
  
  try {
    const response = await api.getArxivDatabase(queryItems.value.keyword); // 发起 API 请求
    
    console.log('完整的响应数据:', response.data); // 调试日志，检查响应数据结构
    
    if (response.data.error) {
      data.value = [];  // 如果有错误，清空表格数据
      message.value = response.data.error;
    } else {
      // 确保获取的数据是期望的数组格式
      data.value = response.data || [];
      const paperCount = data.value.length;  // 获取返回数据的条目数
      console.log('设置后的表格数据:', data.value);  // 再次确认设置的数据结构
      message.value = `数据加载成功，共 ${paperCount} 份论文`;
    }
  } catch (error) {
    console.error('数据加载失败', error);
    message.value = '数据加载失败，请检查网络连接或稍后重试。';
  }
}

// 页面加载时默认获取数据
// onMounted(() => {
//   fetchData()
// })

// 点击跳转到链接的处理函数
const openLink = (url) => {
  if (url) {
    window.open(url, '_blank')  // 打开链接到新标签页
  }
}
</script>

<template>
  <CommonPage>
    <div style="margin-bottom: 1rem;">
      <NInput v-model:value="queryItems.keyword" placeholder="请输入关键词" clearable style="width: 300px;" />
      <NButton @click="fetchData" style="margin-left: 10px;">加载数据</NButton>
    </div>
    
    <div v-if="message">{{ message }}</div> <!-- 显示加载状态或错误信息 -->

    <!-- 表格 -->
    <NDataTable
      :columns="columns"
      :data="data"
    />
  </CommonPage>
</template>
