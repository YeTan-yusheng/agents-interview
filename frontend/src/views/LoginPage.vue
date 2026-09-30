<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const username = ref("");
const password = ref("");
const message = ref("");

async function doLogin() {
  message.value = "登录中...";
  try {
    await auth.login(username.value, password.value);
    await router.push("/user");
  } catch (e) {
    message.value = `失败：${(e as Error).message}`;
  }
}
</script>

<template>
  <h1>登录</h1>
  <input v-model="username" placeholder="用户名" />
  <input v-model="password" type="password" placeholder="密码" />
  <button @click="doLogin">登录</button>
  <p>{{ message }}</p>
</template>


<style>
input {
    display:block; 
    margin:8px 0;
    padding:8px;
}
</style>