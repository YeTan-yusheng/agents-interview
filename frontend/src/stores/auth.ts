import { ref } from 'vue';
import { defineStore } from 'pinia';
import type { TokenResponse, User } from '../types/user';
import { login as loginApi, fetchMe } from '../api/user';


const TOKEN_KEY = "access_token";

export const useAuthStore = defineStore('auth', () => {
    const token = ref<string | null>(localStorage.getItem(TOKEN_KEY));
    const user = ref<User | null>(null);

    async function login(username: string, password: string) {
        const t: TokenResponse = await loginApi({ username, password });
        token.value = t.access_token;
        localStorage.setItem(TOKEN_KEY, t.access_token);
    }

    async function loadMe(){
        if (!token.value) 
            return;
        user.value = await fetchMe(token.value);
    }

    function logout() {
        token.value = null;
        user.value = null;
        localStorage.removeItem(TOKEN_KEY);
    }

    return { token, user, login, loadMe, logout };
})