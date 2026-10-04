export const BASE_URL = "/api";

let onUnauthorized: (() => void) | null = null;

export function setUnauthorizedHandler(fn: () => void) {
  onUnauthorized = fn;
}

/** 流式路径等绕过 request 的调用点，手动触发全局 401 行为（登出+跳登录）。 */
export function handleUnauthorized() {
  onUnauthorized?.();
}


export const TOKEN_KEY = "access_token";


export function authHeaders(): Record<string, string> {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}


export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}


export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    if (res.status === 401) {
      onUnauthorized?.();          // 有注册就执行，没注册跳过（?. 的作用）
    }
    let detail = `请求失败: ${res.status}`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* 响应体不是 JSON 时忽略，用默认提示 */
    }
    throw new ApiError(res.status, detail);
  }

  return res.json() as Promise<T>;
}
