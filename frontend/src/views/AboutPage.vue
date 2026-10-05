<script setup lang="ts">
const stack = [
  "FastAPI", "SQLAlchemy 2 (asyncmy)", "LangGraph", "MySQL",
  "Vue 3 + TypeScript", "Vite", "SSE", "Docker Compose", "Nginx",
];

const highlights = [
  {
    title: "LangGraph 状态机编排",
    desc: "面试官、评分官、种子节点组成状态图，条件边按轮次路由；图管流程，service 管事务。",
  },
  {
    title: "Checkpointer 断点续聊",
    desc: "图状态持久化到 SQLite（挂载数据卷），对话记忆跨进程存活；数据库表降为幂等投影，单向同步。",
  },
  {
    title: "SSE 逐字流式",
    desc: "astream_events 捕获模型 token，经 nginx 反代关闭缓冲后逐字下发；错误双通道（HTTP 状态码 + 流内事件帧）。",
  },
  {
    title: "容器化一键部署",
    desc: "同源 /api 反代消灭 CORS，双阶段镜像，compose 健康检查编排，一条命令起全栈。",
  },
];
</script>

<template>
  <div class="about">
    <div class="card head">
      <h1>AI 模拟面试系统</h1>
      <p class="sub">
        从零实现的全栈 AI 应用：异步后端 + 多角色智能体编排 + 流式交互，
        本页面即是该项目的演示前端。
      </p>
      <div class="chips">
        <span v-for="s in stack" :key="s" class="chip">{{ s }}</span>
      </div>
    </div>

    <div class="card" v-for="h in highlights" :key="h.title">
      <h3>{{ h.title }}</h3>
      <p>{{ h.desc }}</p>
    </div>

    <p class="foot"><RouterLink to="/interview">去开始一场面试 →</RouterLink></p>
  </div>
</template>

<style scoped>
.about { max-width: 680px; margin: 24px auto; padding: 0 16px; }
.head { margin-bottom: 14px; }
h1 { font-size: 22px; margin-bottom: 8px; }
.sub { color: var(--text-2); line-height: 1.7; margin: 0 0 16px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip {
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary);
}
.about > .card {
  margin-bottom: 12px;
  transition: transform 0.15s, box-shadow 0.15s;
}
.about > .card:hover { transform: translateY(-2px); box-shadow: var(--shadow); }
.about h3 { font-size: 16px; margin-bottom: 6px; }
.about p { margin: 0; line-height: 1.7; color: var(--text); }
.foot { text-align: center; margin: 16px 0; }
</style>
