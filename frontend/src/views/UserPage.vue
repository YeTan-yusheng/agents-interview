<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { listInterviews } from "../api/interview";
import type { InterviewOut } from "../types/interview";

const router = useRouter();
const auth = useAuthStore();
const interviews = ref<InterviewOut[]>([]);

const total = computed(() => interviews.value.length);
const ongoing = computed(() => interviews.value.filter(i => i.status === "ongoing").length);
const finished = computed(() => interviews.value.filter(i => i.status === "completed").length);

onMounted(async () => {
  try {
    await auth.loadMe();          // 上站思考题的答案：loadMe 的正式时机
  } catch {
     // 401 已由 client 全局处理（登出+跳转）
  }
  try {
    interviews.value = await listInterviews();
  } catch {
    /* 401 已全局处理；后端不可达时统计留空 */
  }
});
</script>

<template>
  <div class="card home-card">
    <div class="who">
      <div class="avatar">{{ auth.user?.username?.charAt(0).toUpperCase() || "?" }}</div>
      <div>
        <h1>欢迎回来</h1>
        <p class="sub" v-if="auth.user">
          {{ auth.user.username }}（id={{ auth.user.id }}）
        </p>
        <p class="sub" v-else>加载中...</p>
      </div>
    </div>

    <div class="stats">
      <div class="stat">
        <span class="num">{{ total }}</span>
        <span class="label">累计场次</span>
      </div>
      <div class="stat">
        <span class="num num-ongoing">{{ ongoing }}</span>
        <span class="label">进行中</span>
      </div>
      <div class="stat">
        <span class="num num-done">{{ finished }}</span>
        <span class="label">已完成</span>
      </div>
    </div>

    <div class="actions">
      <button class="btn btn-primary" @click="router.push('/interview')">开始面试</button>
      <button class="btn btn-ghost" @click="router.push('/about')">关于本项目</button>
    </div>
  </div>
</template>

<style scoped>
.home-card {
  width: 520px;
  max-width: calc(100vw - 32px);
  margin: 8vh auto 0;
}
.who {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}
.avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #7aa2ff);
  color: #fff;
  font-size: 22px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(47, 107, 255, 0.3);
}
h1 { font-size: 20px; }
.sub { color: var(--text-2); font-size: 14px; margin-top: 2px; }

.stats {
  display: flex;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: 22px;
}
.stat {
  flex: 1;
  text-align: center;
  padding: 14px 8px;
  background: var(--primary-soft-solid);
}
.stat + .stat { border-left: 1px solid var(--border); }
.num { display: block; font-size: 22px; font-weight: 700; color: var(--primary); }
.num-ongoing { color: var(--ok); }
.num-done { color: var(--text-2); }
.label { font-size: 12px; color: var(--text-2); }

.actions { display: flex; gap: 10px; flex-wrap: wrap; }
</style>
