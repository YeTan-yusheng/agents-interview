import { createApp } from "vue";
import { createPinia } from "pinia";
import router from "./router";
import App from "./App.vue";
import { useAuthStore } from "./stores/auth";
import { setUnauthorizedHandler } from "./api/client";


const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount("#app");


const auth = useAuthStore();
setUnauthorizedHandler(() => {
  auth.logout();
  void router.push("/login");
});