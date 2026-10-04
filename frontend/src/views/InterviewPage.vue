<script setup lang="ts">
import { onMounted, ref } from "vue";
import { fetchInterview, listInterviews, startInterview, streamAnswer } from "../api/interview";
import type { InterviewOut } from "../types/interview";

const topic = ref("");
const interview = ref<InterviewOut | null>(null);
const streamingText = ref("");   // 流式气泡：面试官正在说的话
const draft = ref("");
const streaming = ref(false);
const errorText = ref("");
const showStart = ref(true);
const history = ref<InterviewOut[]>([]);   // 历史面试列表（含已结束的，可回看）

onMounted(async () => {
  try {
    history.value = await listInterviews();
  } catch {
    /* 列表加载失败不阻塞开新面试；401 已由全局拦截处理 */
  }
});

async function onNewInterview() {
  errorText.value = "";
  const created = await startInterview({ topic: topic.value });
  interview.value = created;
  history.value = [created, ...history.value];   // 新场次进列表
  showStart.value = false;
}

async function selectInterview(id: number) {
  errorText.value = "";
  interview.value = await fetchInterview(id);
  showStart.value = false;
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
    }],
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
  <div class="page">
    <div v-if="showStart" class="start">
      <input v-model="topic" placeholder="应聘方向，如：Python 后端开发" />
      <button @click="onNewInterview" :disabled="topic.trim().length < 2">开新面试</button>

      <template v-if="history.length">
        <h4>或继续历史面试</h4>
        <ul class="hist">
          <li v-for="it in history" :key="it.id" @click="selectInterview(it.id)">
            <span class="hist-topic">{{ it.topic }}</span>
            <span class="hist-status">{{ it.status === "ongoing" ? "进行中" : "已结束" }}</span>
          </li>
        </ul>
      </template>
    </div>

    <template v-if="interview">
      <h3>{{ interview.topic }}（{{ interview.status === "ongoing" ? "进行中" : "已结束" }}）</h3>

      <div class="msgs">
        <div v-for="m in interview.messages" :key="m.id" :class="['bubble', m.role]">
          {{ m.content }}
        </div>
        <div v-if="streamingText" class="bubble interviewer streaming">{{ streamingText }}▍</div>
      </div>

      <p v-if="errorText" class="err">{{ errorText }}</p>

      <div class="inputbar" v-if="interview.status === 'ongoing'">
        <input v-model="draft" :disabled="streaming"
               @keyup.enter="onSend" placeholder="写下你的回答…" />
        <button @click="onSend" :disabled="streaming || !draft.trim()">
          {{ streaming ? "面试官思考中…" : "发送" }}
        </button>
      </div>

      <div v-if="interview.evaluation" class="eval">
        <h4>总评</h4>
        <p>{{ interview.evaluation }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.msgs { display: flex; flex-direction: column; gap: 8px; max-width: 720px; margin: 12px auto; }
.bubble { padding: 8px 12px; border-radius: 10px; max-width: 72%; white-space: pre-wrap; }
.bubble.interviewer { align-self: flex-start; background: #eef2f7; }
.bubble.candidate { align-self: flex-end; background: #d9ecff; }
.streaming { color: #555; }
.err { color: #c0392b; text-align: center; }
.inputbar { display: flex; gap: 8px; max-width: 720px; margin: 0 auto; }
.inputbar input { flex: 1; padding: 8px; }
.eval { max-width: 720px; margin: 16px auto; background: #f7f9fa; padding: 12px; border-radius: 8px; }
.start { max-width: 720px; margin: 0 auto; text-align: center; }
.hist { list-style: none; padding: 0; max-width: 720px; margin: 8px auto; text-align: left; }
.hist li { display: flex; justify-content: space-between; padding: 8px 12px; border-radius: 8px; cursor: pointer; }
.hist li:hover { background: #f0f4f8; }
.hist-topic { font-weight: 500; }
.hist-status { color: #6b7a90; font-size: 13px; }
</style>
