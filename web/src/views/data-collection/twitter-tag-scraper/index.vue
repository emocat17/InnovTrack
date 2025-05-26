<template>
    <div class="page-container">
        <n-card title="Twitter 标签/关键词数据下载" :bordered="false" class="scraper-card">
            <n-form ref="formRef" :model="formModel" :rules="rules" label-placement="left" label-width="auto"
                require-mark-placement="right-hanging">
                <n-grid :cols="2" :x-gap="24">
                    <n-form-item-gi label="存储关键词 (Keyword)" path="keyword">
                        <n-input v-model:value="formModel.keyword" placeholder="用于创建数据文件夹, e.g., AIResearch" />
                    </n-form-item-gi>
                    <n-form-item-gi label="主要搜索标签 (Tag)" path="tag">
                        <n-input v-model:value="formModel.tag" placeholder="e.g., #ZeroTrust (可选)" />
                    </n-form-item-gi>

                    <n-divider title-placement="left" style="grid-column: 1 / -1;">高级搜索选项 (可选)</n-divider>

                    <n-form-item-gi label="包含所有这些词" path="search_all_these_words">
                        <n-input v_model:value="formModel.search_all_these_words" placeholder="e.g., machine learning" />
                    </n-form-item-gi>
                    <n-form-item-gi label="包含这个精确短语" path="search_exact_phrase">
                        <n-input v-model:value="formModel.search_exact_phrase" placeholder="e.g., future of AI" />
                    </n-form-item-gi>
                    <n-form-item-gi label="包含这些关键词中的任何一个" path="search_any_of_these_keywords">
                        <n-input v-model:value="formModel.search_any_of_these_keywords"
                            placeholder="e.g., innovation breakthrough" />
                    </n-form-item-gi>
                    <n-form-item-gi label="不含这些词" path="search_none_of_these_words">
                        <n-input v-model:value="formModel.search_none_of_these_words" placeholder="e.g., hype rumor" />
                    </n-form-item-gi>
                    <n-form-item-gi label="包含这些标签 (列表)" path="search_hashtags_str">
                        <n-input v-model:value="formModel.search_hashtags_str" placeholder="e.g., #Tech, #AI (逗号分隔)" />
                        <template #feedback>输入多个标签请用英文逗号分隔</template>
                    </n-form-item-gi>
                    <n-form-item-gi label="来自该用户" path="search_from_user">
                        <n-input v-model:value="formModel.search_from_user" placeholder="e.g., elonmusk (不带@)" />
                    </n-form-item-gi>
                    <n-form-item-gi label="起始日期 (Since)" path="search_since_date">
                        <n-date-picker v-model:formatted-value="formModel.search_since_date" type="date"
                            value-format="yyyy-MM-dd" clearable style="width: 100%;" />
                    </n-form-item-gi>
                    <n-form-item-gi label="截止日期 (Until)" path="search_until_date">
                        <n-date-picker v-model:formatted-value="formModel.search_until_date" type="date"
                            value-format="yyyy-MM-dd" clearable style="width: 100%;" />
                    </n-form-item-gi>

                    <n-divider title-placement="left" style="grid-column: 1 / -1;">下载设置</n-divider>

                    <n-form-item-gi label="下载数量" path="down_count">
                        <n-input-number v-model:value="formModel.down_count" :min="20" :step="20" style="width: 100%;" />
                    </n-form-item-gi>
                    <n-form-item-gi label="最大并发下载" path="max_concurrent_requests">
                        <n-input-number v-model:value="formModel.max_concurrent_requests" :min="1" :max="10"
                            style="width: 100%;" />
                    </n-form-item-gi>

                    <n-form-item-gi label="下载类型" path="text_down" :span="2">
                        <n-radio-group v-model:value="formModel.text_down" name="downloadType">
                            <n-radio-button :value="false">下载媒体 (图片/视频)</n-radio-button>
                            <n-radio-button :value="true">仅下载文本</n-radio-button>
                        </n-radio-group>
                    </n-form-item-gi>

                    <n-form-item-gi v-if="!formModel.text_down" label="媒体来源标签页" path="media_latest" :span="2">
                        <n-radio-group v-model:value="formModel.media_latest" name="mediaSourceTab">
                            <n-radio-button :value="true">'最新' 标签页</n-radio-button>
                            <n-radio-button :value="false">'媒体' 标签页</n-radio-button>
                        </n-radio-group>
                    </n-form-item-gi>
                    <n-form-item-gi label="过滤链接" path="search_filter_links" :span="1">
                        <n-switch v-model:value="formModel.search_filter_links" />
                        <template #feedback>为True时添加 filter:links (通常用于媒体下载)</template>
                    </n-form-item-gi>
                    <n-form-item-gi label="排除回复" path="search_exclude_replies" :span="1">
                        <n-switch v-model:value="formModel.search_exclude_replies" />
                        <template #feedback>为True时添加 -filter:replies</template>
                    </n-form-item-gi>

                </n-grid>

                <n-space justify="center" style="margin-top: 20px;">
                    <n-button type="primary" @click="handleSubmit" :loading="loading">开始下载</n-button>
                </n-space>
            </n-form>
        </n-card>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import {
    NCard, NForm, NFormItemGi, NInput, NInputNumber, NDatePicker,
    NSwitch, NButton, NSpace, NDivider, NGrid, useMessage,
    NRadioGroup, NRadioButton
} from 'naive-ui'
import api from '@/api' // Your API import

const message = useMessage()
const formRef = ref(null)
const loading = ref(false)

const formModel = reactive({
    keyword: '',
    tag: null,
    search_all_these_words: null,
    search_exact_phrase: null,
    search_any_of_these_keywords: null,
    search_none_of_these_words: null,
    search_hashtags_str: null, // Comma-separated string for hashtags
    search_from_user: null,
    search_filter_links: true,
    search_exclude_replies: true,
    search_until_date: null,
    search_since_date: null,
    down_count: 100,
    media_latest: true,
    text_down: false,
    max_concurrent_requests: 2,
})

const rules = {
    keyword: {
        required: true,
        message: '请输入存储关键词',
        trigger: ['input', 'blur'],
    },
    down_count: {
        type: 'number',
        required: true,
        message: '请输入下载数量',
        trigger: ['input', 'blur'],
    },
    max_concurrent_requests: {
        type: 'number',
        required: true,
        message: '请输入最大并发数',
        trigger: ['input', 'blur'],
    }
}

const handleSubmit = async () => {
    try {
        await formRef.value?.validate()
        loading.value = true
        message.info('正在提交下载任务...')

        // Prepare payload
        const payload = { ...formModel }

        // Convert comma-separated hashtags string to array
        if (payload.search_hashtags_str && payload.search_hashtags_str.trim() !== '') {
            payload.search_hashtags = payload.search_hashtags_str.split(',').map(h => h.trim()).filter(h => h.startsWith('#'));
        } else {
            payload.search_hashtags = null; // Ensure it's null if empty or not provided
        }
        delete payload.search_hashtags_str; // Remove the temporary string field

        // Remove null or empty string values for optional fields to keep payload clean
        for (const key in payload) {
            if (payload[key] === null || payload[key] === '') {
                // Keep boolean false values and number 0
                if (typeof payload[key] !== 'boolean' && typeof payload[key] !== 'number') {
                    delete payload[key];
                }
            }
        }

        console.log("Sending payload:", payload)
        const response = await api.runTwitterTagScraper(payload) // Call the API

        if (response.msg) { // Assuming your Success model has a 'msg' field
            message.success(response.msg || 'Twitter下载任务已成功启动！请关注服务器日志。')
        } else {
            message.success('Twitter下载任务已成功启动！请关注服务器日志。')
        }

    } catch (error) {
        console.error('提交下载任务失败:', error)
        if (error.response && error.response.data && error.response.data.detail) {
            if (Array.isArray(error.response.data.detail)) {
                message.error('表单验证失败: ' + error.response.data.detail.map(d => `${d.loc[1]}: ${d.msg}`).join('; '));
            } else if (typeof error.response.data.detail === 'string') {
                message.error('提交失败: ' + error.response.data.detail);
            } else {
                message.error('提交下载任务失败，请检查网络或联系管理员。')
            }
        } else {
            message.error(error.message || '提交下载任务失败，请检查网络或联系管理员。')
        }
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.page-container {
    padding: 20px;
}

.scraper-card {
    max-width: 1000px;
    /* Adjust as needed */
    margin: 0 auto;
}
</style>