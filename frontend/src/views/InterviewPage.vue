<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import { fetchInterview, listInterviews, startInterview, streamAnswer } from "../api/interview";
import type { InterviewOut, MessageOut } from "../types/interview";

const topic = ref("");
const interview = ref<InterviewOut | null>(null);
const streamingText = ref("");   // 流式气泡：面试官正在说的话
const draft = ref("");
const streaming = ref(false);
const errorText = ref("");
const history = ref<InterviewOut[]>([]);   // 历史面试列表（含已结束的，可回看）
const msgsEl = ref<HTMLElement | null>(null);

onMounted(async () => {
  try {
    history.value = await listInterviews();
  } catch {
    /* 列表加载失败不阻塞开新面试；401 已由全局拦截处理 */
  }
});

function fmtTime(iso: string | undefined): string {
  return iso ? iso.slice(11, 16) : "";
}

// 新消息 / 流式追加时自动滚到底部
watch(
  () => [interview.value?.messages.length, streamingText.value],
  () => {
    void nextTick(() => {
      msgsEl.value?.scrollTo({ top: msgsEl.value.scrollHeight });
    });
  },
);

function backToStart() {
  interview.value = null;
  errorText.value = "";
}

async function onNewInterview() {
  errorText.value = "";
  const created = await startInterview({ topic: topic.value });
  interview.value = created;
  history.value = [created, ...history.value];   // 新场次进列表
}

async function selectInterview(id: number) {
  errorText.value = "";
  interview.value = await fetchInterview(id);
}

async function onSend() {
  if (!interview.value || !draft.value.trim() || streaming.value) return;
  const content = draft.value.trim();
  draft.value = "";
  streaming.value = true;
  errorText.value = "";
  streamingText.value = "";

  // 乐观上屏：自己的回答立刻可见，end 的全量覆盖兜底
  interview.value = {
    ...interview.value,
    messages: [...interview.value.messages, {
      id: -Date.now(), role: "candidate", content,
      created_at: new Date().toISOString(),
    } as MessageOut],
  };

  try {
    await streamAnswer(interview.value.id, content, (ev) => {
      if (ev.type === "token") {
        streamingText.value += ev.content;
      } else if (ev.type === "end") {
        interview.value = ev.interview;   // 全量覆盖 = 唯一事实
        streamingText.value = "";
      } else {
        errorText.value = ev.message;
        streamingText.value = "";
      }
    });
  } catch {
    errorText.value = "连接中断，请稍后重试";
  } finally {
    streaming.value = false;
  }
}
</script>

<template>
  <div class="iv-page">
    <!-- ===== 开场面板 ===== -->
    <div v-if="!interview" class="card start-card">
      <h1>AI 模拟面试</h1>
      <p class="sub">输入应聘方向，面试官将结合你的回答持续追问</p>

      <div class="field new-row">
        <input v-model="topic" class="input" placeholder="应聘方向，如：Python 后端开发"
               @keyup.enter="onNewInterview" />
        <button class="btn btn-primary" :disabled="topic.trim().length < 2">开新面试</button>
      </div>

      <template v-if="history.length">
        <h4 class="hist-title">或继续历史面试</h4>
        <ul class="hist">
          <li v-for="it in history" :key="it.id" @click="selectInterview(it.id)">
            <span class="hist-topic">{{ it.topic }}</span>
            <span class="hist-status" :class="it.status">
              {{ it.status === "ongoing" ? "进行中" : "已结束" }}
            </span>
          </li>
        </ul>
      </template>
    </div>

    <!-- ===== 面试视图 ===== -->
    <template v-else>
      <header class="iv-head">
        <button class="btn btn-ghost back" @click="backToStart">←</button>
        <div class="iv-title">
          <span class="iv-topic">{{ interview.topic }}</span>
          <span class="pill" :class="interview.status">
            {{ interview.status === "ongoing" ? "进行中" : "已结束" }}
          </span>
        </div>
      </header>

      <div ref="msgsEl" class="msgs">
        <div v-for="m in interview.messages" :key="m.id"
             class="row" :class="m.role === 'interviewer' ? 'row-l' : 'row-r'">
          <div class="bubble" :class="m.role">
            <div class="meta">
              <span class="who">{{ m.role === "interviewer" ? "面试官" : "我" }}</span>
              <span class="time">{{ fmtTime(m.created_at) }}</span>
            </div>
            {{ m.content }}
          </div>
        </div>

        <div v-if="streamingText" class="row row-l">
          <div class="bubble interviewer">
            <div class="meta"><span class="who">面试官</span></div>
            {{ streamingText }}<span class="caret">▍</span>
          </div>
        </div>

        <div v-if="interview.evaluation" class="eval">
          <h4>面试总评</h4>
          <p>{{ interview.evaluation }}</p>
        </div>
      </div>

      <p v-if="errorText" class="err">{{ errorText }}</p>

      <div class="inputbar" v-if="interview.status === 'ongoing'">
        <input v-model="draft" class="input" :disabled="streaming"
               @keyup.enter="onSend" placeholder="写下你的回答…" />
        <button class="btn btn-primary send" @click="onSend"
                :disabled="streaming || !draft.trim()">
          {{ streaming ? "思考中…" : "发送" }}
        </button>
      </div>
      <p v-else class="hint ended-hint">本场已结束，回到开场面板可查看历史与总评</p>
    </template>
  </div>
</template>

<style scoped>
.iv-page {
  max-width: 820px;
  margin: 0 auto;
  padding: 16px 16px 12px;
  /* 扣掉壳层的吸顶导航与页脚，让聊天区正好占满一屏 */
  height: calc(100svh - 156px);
  min-height: 480px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

/* --- 开场面板 --- */
.start-card {
  margin-top: 10vh;
  text-align: center;
}
.start-card h1 { font-size: 24px; margin-bottom: 6px; }
.start-card .sub { color: var(--text-2); font-size: 14px; margin-bottom: 22px; }
.new-row { display: flex; gap: 10px; }
.new-row .input { flex: 1; }
.hist-title {
  margin: 26px 0 8px;
  font-size: 14px;
  color: var(--text-2);
  text-align: left;
}
.hist { list-style: none; padding: 0; margin: 0; text-align: left; }
.hist li {
  display: flex;
  justify-content: space-between;
  padding: 11px 14px;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.hist li:hover { border-color: var(--primary); background: var(--primary-soft); }
.hist-topic { font-weight: 500; }
.hist-status { font-size: 13px; color: var(--text-2); }
.hist-status.ongoing { color: var(--ok, #16a34a); }

/* --- 头部 --- */
.iv-head {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}
.back { padding: 6px 12px; }
.iv-title { display: flex; align-items: center; gap: 10px; min-width: 0; }
.iv-topic { font-weight: 600; font-size: 17px; }
.pill {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--primary-soft);
  color: var(--primary);
  white-space: nowrap;
}
.pill.completed { background: var(--primary-soft-solid); color: var(--text-2); }

/* --- 消息区 --- */
.msgs {
  flex: 1;
  overflow-y: auto;
  padding: 18px 4px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.row { display: flex; animation: fade-up 0.22s ease both; }
.row-l { justify-content: flex-start; }
.row-r { justify-content: flex-end; }
.bubble {
  max-width: 76%;
  padding: 10px 14px;
  border-radius: 14px;
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 15px;
}
.bubble { box-shadow: var(--shadow-sm); }
.bubble.interviewer {
  background: var(--surface);
  border: 1px solid var(--border);
  border-top-left-radius: 4px;
}
.bubble.candidate {
  background: linear-gradient(135deg, var(--primary), #5c8cff);
  color: #fff;
  border-top-right-radius: 4px;
}
.bubble .meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  margin-bottom: 4px;
  opacity: 0.65;
}
.bubble.candidate .meta { color: rgba(255, 255, 255, 0.8); }
.caret { animation: blink 1s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }

/* --- 总评 --- */
.eval {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--primary);
  border-radius: 10px;
  padding: 14px 16px;
}
.eval h4 { margin-bottom: 6px; font-size: 14px; color: var(--primary); }
.eval p { margin: 0; line-height: 1.7; }

/* --- 输入区 --- */
.err { text-align: center; }
.inputbar { display: flex; gap: 10px; padding-top: 10px; }
.inputbar .input { flex: 1; }
.send { min-width: 92px; }
.ended-hint { text-align: center; padding: 8px 0 4px; }
</style>
