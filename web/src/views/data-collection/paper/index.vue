<!-- views/data-collection/paper/index.vue -->

<template>
    <div>
        <h1>论文收集</h1>
        <!-- 添加按钮 -->
        <button @click="toggleMessage">点击显示/隐藏 HelloWorld</button>

        <!-- 控制显示的文本 -->
        <p v-if="showMessage">HelloWorld</p>
    </div>
</template>

<script setup>
import { ref } from 'vue';

// 定义响应式数据 showMessage 用于控制显示状态
const showMessage = ref(false);

// 点击按钮切换 showMessage 的值
function toggleMessage() {
    showMessage.value = !showMessage.value;
}
</script>

<style scoped>
/* 可根据需要定义样式 */
button {
    margin-top: 20px;
    padding: 10px 15px;
    font-size: 16px;
    cursor: pointer;
}

p {
    margin-top: 20px;
    font-size: 18px;
    color: #333;
}
</style>
