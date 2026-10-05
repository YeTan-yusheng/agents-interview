<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const auth = useAuthStore();
const username = ref("");
const password = ref("");
const error = ref("");
const busy = ref(false);

async function doLogin() {
  if (busy.value) return;
  error.value = "";
  busy.value = true;
  try {
    await auth.login(username.value, password.value);
    await router.push("/user");
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <div class="card auth-card fade-up">
    <div class="brand">面</div>
    <h1>AI 模拟面试系统</h1>
    <p class="sub">登录以开始你的模拟面试</p>

    <form @submit.prevent="doLogin">
      <div class="field">
        <label for="username">用户名</label>
        <input id="username" v-model="username" class="input" autocomplete="username" />
      </div>
      <div class="field">
        <label for="password">密码</label>
        <input id="password" v-model="password" class="input" type="password"
               autocomplete="current-password" />
      </div>
      <p v-if="error" class="err">{{ error }}</p>
      <button class="btn btn-primary btn-block" :disabled="busy || !username.trim() || !password">
        {{ busy ? "登录中…" : "登录" }}
      </button>
    </form>

    <p class="links">
      没有账号？<RouterLink to="/register">去注册</RouterLink>
    </p>
  </div>
</template>

<style scoped>
.brand {
  width: 54px;
  height: 54px;
  margin: 0 auto 16px;
  border-radius: 15px;
  background: linear-gradient(135deg, var(--primary), #7aa2ff);
  color: #fff;
  font-size: 26px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 6px 18px rgba(47, 107, 255, 0.35);
}
</style>
