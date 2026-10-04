import type {InterviewCreate, InterviewOut, AnswerCreate, InterviewStreamEvent} from "../types/interview.ts";
import {ApiError, request} from "./client.ts";

export function startInterview(data: InterviewCreate, token: string): Promise<InterviewOut> {
  return request<InterviewOut>("/interview", {
    method: "POST",
    body: JSON.stringify(data),
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function fetchInterview(id: number, token: string): Promise<InterviewOut> {
  return request<InterviewOut>(`/interview/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function submitAnswer(
  interviewId: number,
  data: AnswerCreate,
  token: string,
): Promise<InterviewOut> {
  return request<InterviewOut>(`/interview/${interviewId}/answer`, {
    method: "POST",
    body: JSON.stringify(data),
    headers: { Authorization: `Bearer ${token}` },
  });
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
      Authorization: `Bearer ${localStorage.getItem("access_token") ?? ""}`,
    },
    body: JSON.stringify({ content } satisfies AnswerCreate),
  });
  if (!resp.ok || !resp.body) throw new ApiError(resp.status, "请求失败");   // 按你 ApiError 实际签名调

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
