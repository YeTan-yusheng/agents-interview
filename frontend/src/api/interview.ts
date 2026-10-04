import type {InterviewCreate, InterviewOut, AnswerCreate, InterviewStreamEvent} from "../types/interview.ts";
import {ApiError, request, authHeaders, handleUnauthorized} from "./client.ts";

export function startInterview(data: InterviewCreate): Promise<InterviewOut> {
  return request<InterviewOut>("/interview", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function fetchInterview(id: number): Promise<InterviewOut> {
  return request<InterviewOut>(`/interview/${id}`);
}

export function listInterviews(): Promise<InterviewOut[]> {
  return request<InterviewOut[]>("/interview");
}


export async function streamAnswer(
  interviewId: number,
  content: string,
  onEvent: (ev: InterviewStreamEvent) => void,
): Promise<void> {
  const resp = await fetch(`${import.meta.env.VITE_API_BASE}/interview/${interviewId}/answer`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify({ content } satisfies AnswerCreate),
  });
  if (!resp.ok || !resp.body) {
    if (resp.status === 401) handleUnauthorized();   // 流式路径手动接回全局拦截（登出+跳登录）
    throw new ApiError(resp.status, "请求失败");
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const parts = buf.split("\n\n");      // 帧以空行分隔
    buf = parts.pop() ?? "";              // 尾段可能不完整，留到下一轮拼
    for (const p of parts) {
      if (!p.startsWith("data: ")) continue;
      onEvent(JSON.parse(p.slice(6)) as InterviewStreamEvent);
    }
  }
}
