import type {InterviewCreate, InterviewOut} from "../types/interview.ts";
import {request} from "./client.ts";

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
