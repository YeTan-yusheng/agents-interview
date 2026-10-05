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
const error = ref("");
const busy = ref(false);

async function doRegister() {
  if (busy.value) return;
  error.value = "";
  if (password.value !== password2.value) {
    error.value = "两次输入的密码不一致";
    return;
  }
  busy.value = true;
  try {
    // 契约：POST /api/users —— username 2~20 位 \w+，password 6~72 位
    await createUser({ username: username.value, password: password.value });
    await auth.login(username.value, password.value);   // 注册即登录
    await router.push("/user");
  } catch (e) {
    error.value = (e as Error).message;   // 如「用户名xxx已存在」(409)
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <div class="card auth-card fade-up">
    <div class="brand">面</div>
    <h1>创建账号</h1>
    <p class="sub">注册后立即开始第一场模拟面试</p>

    <form @submit.prevent="doRegister">
      <div class="field">
        <label for="r-username">用户名（2~20 位字母/数字/下划线）</label>
        <input id="r-username" v-model="username" class="input" autocomplete="username" />
      </div>
      <div class="field">
        <label for="r-password">密码（至少 6 位）</label>
        <input id="r-password" v-model="password" class="input" type="password"
               autocomplete="new-password" />
      </div>
      <div class="field">
        <label for="r-password2">确认密码</label>
        <input id="r-password2" v-model="password2" class="input" type="password"
               autocomplete="new-password" />
      </div>
      <p v-if="error" class="err">{{ error }}</p>
      <button class="btn btn-primary btn-block"
              :disabled="busy || !username.trim() || !password || !password2">
        {{ busy ? "注册中…" : "注册并登录" }}
      </button>
    </form>

    <p class="links">
      已有账号？<RouterLink to="/login">去登录</RouterLink>
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
