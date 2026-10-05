<script setup lang="ts">
import { computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "./stores/auth";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const navs = [
  { path: "/user", label: "主页" },
  { path: "/interview", label: "模拟面试" },
  { path: "/about", label: "关于" },
];

const initial = computed(() => {
  const name = auth.user?.username || "";
  return name ? name.slice(0, 1).toUpperCase() : "?";
});

function isActive(path: string): boolean {
  if (path === "/user") return route.path === "/user" || route.path === "/";
  return route.path.startsWith(path);
}

function doLogout() {
  auth.logout();
  void router.push("/login");
}

// 切换路由回到页顶：否则从滚到底的长列表进短页面，视口卡在底部像「点了没反应」
watch(
  () => route.path,
  () => {
    window.scrollTo({ top: 0 });
  },
);
</script>

<template>
  <div class="shell">
    <!-- 吸顶导航 -->
    <header class="topbar">
      <div class="topbar-in">
        <RouterLink to="/user" class="brand">
          <span class="brand-mark">面</span>
          <span class="brand-text">
            <span class="brand-name">AI 模拟面试</span>
            <span class="brand-sub">LangGraph 多角色智能面试</span>
          </span>
        </RouterLink>

        <!-- 胶囊导航：当前页高亮渐变胶囊 -->
        <nav class="capsule">
          <RouterLink v-for="n in navs" :key="n.path" :to="n.path"
                      class="cap" :class="{ active: isActive(n.path) }">
            {{ n.label }}
          </RouterLink>
        </nav>

        <!-- 账号区：未登录给入口，已登录给昵称 + 退出 -->
        <div class="account">
          <template v-if="auth.token">
            <span class="who" :title="auth.user?.username || ''">
              <span class="mini-avatar">{{ initial }}</span>
              <span class="who-name">{{ auth.user?.username }}</span>
            </span>
            <button class="acct-btn" @click="doLogout">退出</button>
          </template>
          <RouterLink v-else to="/login" class="acct-btn login">登录 / 注册</RouterLink>
        </div>
      </div>
    </header>

    <!-- 主体 -->
    <main class="main">
      <RouterView />
    </main>

    <!-- 页脚 -->
    <footer class="foot">
      <div class="foot-in">
        <span>AI 模拟面试 · LangGraph 状态机 × SSE 流式 × 容器化部署</span>
        <span class="foot-dim">从零手写的全栈实战项目</span>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.shell {
  min-height: 100svh;
  display: flex;
  flex-direction: column;
}

/* --- 吸顶导航 --- */
.topbar {
  position: sticky;
  top: 0;
  z-index: 40;
  border-bottom: 1px solid var(--border);
  background: var(--surface-glass);
  backdrop-filter: blur(12px);
}
.topbar-in {
  max-width: 1080px;
  margin: 0 auto;
  padding: 9px 20px;
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  color: var(--text);
}
.brand:hover { text-decoration: none; }
.brand-mark {
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  border-radius: 13px;
  background: linear-gradient(135deg, var(--primary), #7aa2ff);
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(47, 107, 255, 0.3);
}
.brand-text { display: flex; flex-direction: column; line-height: 1.25; }
.brand-name { font-weight: 700; font-size: 15px; }
.brand-sub { font-size: 11px; color: var(--text-2); }

/* 胶囊导航 */
.capsule {
  display: flex;
  gap: 4px;
  padding: 4px;
  margin-left: auto;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  box-shadow: var(--shadow-sm);
}
.cap {
  padding: 7px 18px;
  border-radius: 999px;
  font-size: 14px;
  color: var(--text-2);
  white-space: nowrap;
  transition: color 0.15s, background 0.15s;
}
.cap:hover { color: var(--primary); text-decoration: none; }
.cap.active {
  background: linear-gradient(135deg, var(--primary), #5c8cff);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(47, 107, 255, 0.3);
}
.cap.active:hover { color: #fff; }

/* 账号区 */
.account { display: flex; align-items: center; gap: 8px; }
.who {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px 5px 6px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  font-size: 13px;
  color: var(--text-2);
}
.mini-avatar {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #7aa2ff);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.who-name {
  max-width: 96px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.acct-btn {
  padding: 6px 14px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--surface);
  font-size: 13px;
  color: var(--text-2);
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
  text-decoration: none;
}
.acct-btn:hover { border-color: var(--primary); color: var(--primary); text-decoration: none; }
.acct-btn.login {
  background: linear-gradient(135deg, var(--primary), #5c8cff);
  color: #fff;
  border: none;
  font-weight: 600;
}

/* --- 主体与页脚 --- */
.main { flex: 1; }
.foot { background: #161b27; color: #8b93a7; }
.foot-in {
  max-width: 1080px;
  margin: 0 auto;
  padding: 16px 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: space-between;
  font-size: 12px;
}
.foot-dim { color: #5b6478; }

/* --- 窄屏 --- */
@media (max-width: 640px) {
  .topbar-in { padding: 8px 12px; gap: 10px; }
  .brand-sub { display: none; }
  .capsule { order: 3; width: 100%; justify-content: center; margin-left: 0; }
  .who-name { display: none; }
}
</style>
