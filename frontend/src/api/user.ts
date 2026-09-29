import { request } from "./client";
import type {
  User,
  CreateUserRequest,
  LoginRequest,
  TokenResponse,
} from "../types/user";

export function createUser(data: CreateUserRequest): Promise<User> {
  return request<User>("/users", { method: "POST", body: JSON.stringify(data) });
}

export function login(data: LoginRequest): Promise<TokenResponse> {
  return request<TokenResponse>("/users/login", { method: "POST", body: JSON.stringify(data) });
}

export function fetchMe(token: string): Promise<User> {
  return request<User>("/users/me", { headers: { Authorization: `Bearer ${token}` } });
}

export function listUsers(): Promise<User[]> {
  return request<User[]>("/users");
}
