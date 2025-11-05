<template>
  <div>
    <div class="header">
      <StatusIcon :connected="user.connected" />
      {{ user.username }}
    </div>

    <ul class="messages">
      <li
        v-for="(message, index) in user.messages"
        :key="index"
        class="message"
      >
        <div v-if="displaySender(message, index)" class="sender">
          {{ message.fromSelf ? "(yourself)" : user.username }}
        </div>
        {{ message.content }}
      </li>
    </ul>

    <form @submit.prevent="onSubmit" class="form">
      <textarea
        v-model="input"
        placeholder="Your message..."
        class="input"
      />
      <button :disabled="!isValid" class="send-button">Send</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import StatusIcon from "./StatusIcon.vue";

// ---------- Types ----------
interface Message {
  content: string;
  fromSelf: boolean;
}

interface UserType {
  userID: string;
  username: string;
  connected: boolean;
  messages: Message[];
}

// ---------- Props ----------
const props = defineProps<{
  user: UserType;
}>();

// ---------- Emits ----------
const emit = defineEmits<{
  (e: "input", message: string): void;
}>();

// ---------- State ----------
const input = ref("");

// ---------- Computed ----------
const isValid = computed(() => input.value.trim().length > 0);

// ---------- Methods ----------
function onSubmit() {
  if (!isValid.value) return;
  emit("input", input.value.trim());
  input.value = "";
}

function displaySender(message: Message, index: number): boolean {
  if (index === 0) return true;
  const prevMessage = props.user.messages[index - 1];
  return prevMessage ? prevMessage.fromSelf !== message.fromSelf : true;
}
</script>

<style scoped>
.header {
  line-height: 40px;
  padding: 10px 20px;
  border-bottom: 1px solid #dddddd;
}

.messages {
  margin: 0;
  padding: 20px;
}

.message {
  list-style: none;
}

.sender {
  font-weight: bold;
  margin-top: 5px;
}

.form {
  padding: 10px;
}

.input {
  width: 80%;
  resize: none;
  padding: 10px;
  line-height: 1.5;
  border-radius: 5px;
  border: 1px solid #000;
}

.send-button {
  vertical-align: top;
}
</style>
