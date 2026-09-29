<script setup lang="ts">
import { ref } from "vue";
import { useAuthStore } from "./stores/auth";

const auth = useAuthStore();
const username = ref("zhangsan");
const password = ref("");
const message = ref("");

async function doLogin() {
  message.value = "登录中...";
  try {
    await auth.login(username.value, password.value);
    await auth.loadMe();
    message.value = `欢迎，${auth.user?.username}`;
  } catch (e) {
    message.value = `失败：${(e as Error).message}`;
  }
}


async function doLogout() {
  message.value = "退出登录中...";
  try {
    auth.logout();
    message.value = "已退出登录";
  } catch (e) {
    message.value = `失败：${(e as Error).message}`;
  }
}
</script>


<template>
  <h1>登录测试</h1>
  <input v-model="username" placeholder="用户名" />
  <input v-model="password" type="password" placeholder="密码" />
  <button @click="doLogin">登录</button>
  <button @click="doLogout">退出登录</button>
  <p>{{ message }}</p>
</template>
