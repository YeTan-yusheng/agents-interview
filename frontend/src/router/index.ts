import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/user" },
    { path: "/login", component: () => import("../views/LoginPage.vue") },
    { path: "/register", component: () => import("../views/RegisterPage.vue") },
    { path: "/user", component: () => import("../views/UserPage.vue"), meta: { requiresAuth: true } },
    { path: "/about", component: () => import("../views/AboutPage.vue") },
    { path: "/interview",name: "interview",component: () => import("../views/InterviewPage.vue"),meta: { requiresAuth: true }},
  ],
});

router.beforeEach((to) => {
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.token) {
    return "/login";
  }

  if (to.path === "/login" && auth.token) {
    return "/user";
  }
});

export default router;
