<template>
  <div class="login">
    <form @submit.prevent="onSubmit">
      <input
        v-model="username"
        placeholder="Your username..."
        class="input"
      />
      <input
        v-model="password"
        placeholder="Your password..."
        type="password"
        class="input"
      />
      <button :disabled="!isValid" class="button">Send</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";

// ---------- Emits ----------
const emit = defineEmits<{
  (e: "input", username: string, password: string): void;
}>();

// ---------- State ----------
const username = ref("");
const password = ref("");

// ---------- Computed ----------
const isValid = computed(() => {
  return username.value.trim().length > 2 && password.value.trim().length >= 6;
});

// ---------- Methods ----------
function onSubmit() {
  if (!isValid.value) return;
  emit("input", username.value.trim(), password.value.trim());
  username.value = "";
  password.value = "";
}
</script>

<style scoped>
.login {
  width: 300px;
  margin: 200px auto 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.input {
  display: block;
  width: 100%;
  margin-bottom: 10px;
  padding: 8px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.button {
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
}
</style>
