<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { createUser } from "../api/user";

const router = useRouter();
const auth = useAuthStore();
const username = ref("");
const password = ref("");
const password2 = ref("");
const message = ref("");
const busy = ref(false);

async function doRegister() {
  if (busy.value) return;
  message.value = "";
  if (password.value !== password2.value) {
    message.value = "两次输入的密码不一致";
    return;
  }
  busy.value = true;
  try {
    // 契约：POST /api/users —— username 2~20 位 \w+，password 6~72 位
    await createUser({ username: username.value, password: password.value });
    await auth.login(username.value, password.value);   // 注册即登录
    await router.push("/user");
  } catch (e) {
    message.value = `失败：${(e as Error).message}`;   // 如「用户名xxx已存在」(409)
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <h1>注册</h1>
  <p class="hint">用户名：2~20 位字母/数字/下划线；密码：至少 6 位</p>
  <input v-model="username" placeholder="用户名" />
  <input v-model="password" type="password" placeholder="密码" />
  <input v-model="password2" type="password" placeholder="再输一遍密码" />
  <button @click="doRegister" :disabled="busy">{{ busy ? "注册中…" : "注册并登录" }}</button>
  <p>{{ message }}</p>
  <RouterLink to="/login">已有账号？去登录</RouterLink>
</template>

<style>
input {
    display: block;
    margin: 8px 0;
    padding: 8px;
}
.hint { color: #6b7a90; font-size: 13px; }
</style>
