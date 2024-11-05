<script setup>
import { onMounted, ref } from 'vue'
import { NInput, NButton } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import CrudTable from '@/components/table/CrudTable.vue'

import api from '@/api'

defineOptions({ name: '论文数据库展示' })

const $table = ref(null)
const queryItems = ref({})

const columns = [
  {
    title: '发布日期',
    key: '发布日期',
    width: 'auto',
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '标题',
    key: '标题',
    width: 'auto',
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '作者',
    key: '作者',
    align: 'center',
    width: 'auto',
    ellipsis: { tooltip: true },
  },
  {
    title: '摘要',
    key: '摘要',
    align: 'center',
    width: 'auto',
    ellipsis: { tooltip: true },
  },
  {
    title: '链接',
    key: '链接',
    align: 'center',
    width: 'auto',
    ellipsis: { tooltip: true },
  },
  {
    title: 'PDF链接',
    key: 'PDF链接',
    align: 'center',
    width: 'auto',
    ellipsis: { tooltip: true },
  },
]

const data = ref([])

// 获取Data文件夹中的数据（从后端接口）
const fetchData = async (keyword) => {
  try {
    const response = await api.fetchArxivData(keyword)
    // 假设后端返回的数据是excel文件中的内容
    data.value = response.data // 根据后端返回的数据格式进行处理
    $table.value?.handleSearch()
  } catch (error) {
    console.error('数据加载失败', error)
  }
}

onMounted(() => {
  // 你可以选择在页面加载时默认加载某个关键词的数据，或者让用户输入
  fetchData('zero trust') // 使用你爬取的关键字，例：'zero trust'
})
</script>

<template>
  <!-- 业务页面 -->
  <CommonPage>
    <div>
      <NInput
      
        v-model:value="queryItems.keyword"
        placeholder="请输入关键词" 
        clearable
        @keypress.enter="$table?.handleSearch()"
        style="width: 200px;"
      />
      <NButton @click="fetchData(queryItems.keyword)" style="margin-left: 10px;">
        加载数据
      </NButton>
    </div>

    <!-- 表格 -->
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :data="data"
    >
      <template #queryBar>
        <QueryBarItem label="关键字" :label-width="70">
          <NInput
            v-model:value="queryItems.keyword"
            clearable
            type="text"
            placeholder="请输入关键词"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
      </template>
    </CrudTable>
  </CommonPage>
</template>
