<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const message = ref("");

onMounted(async () => {
  try {
    await auth.loadMe();          // 上站思考题的答案：loadMe 的正式时机
  } catch {
     // 401 已由 client 全局处理（登出+跳转）
  }
});

function doLogout() {
  auth.logout();
  void router.push("/login");
}
</script>

<template>
  <h1>我的主页</h1>
  <p v-if="auth.user">欢迎，{{ auth.user.username }}（id={{ auth.user.id }}）</p>
  <p v-else>加载中...</p>
  <button @click="doLogout">退出登录</button>
  <p>{{ message }}</p>
  <RouterLink to="/about">关于</RouterLink>

</template>
