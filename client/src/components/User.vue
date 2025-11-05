<template>
  <div class="user" @click="onClick" :class="{ selected }">
    <div class="description">
      <div class="name">
        {{ user.username }} {{ user.self ? " (yourself)" : "" }}
      </div>
      <div class="status">
        <StatusIcon :connected="user.connected" />{{ status }}
      </div>
    </div>
    <div v-if="user.hasNewMessages" class="new-messages">!</div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import StatusIcon from "./StatusIcon.vue";

// ---------- Types ----------
interface UserType {
  userID: string;
  username: string;
  connected: boolean;
  self?: boolean;
  hasNewMessages?: boolean;
}

// ---------- Props ----------
const props = defineProps<{
  user: UserType;
  selected: boolean;
}>();

// ---------- Emits ----------
const emit = defineEmits<{
  (e: "select"): void;
}>();

// ---------- Methods ----------
function onClick() {
  emit("select");
}

// ---------- Computed ----------
const status = computed(() => (props.user.connected ? "online" : "offline"));
</script>

<style scoped>
.selected {
  background-color: #1164a3;
}

.user {
  padding: 10px;
  cursor: pointer;
}

.description {
  display: inline-block;
}

.status {
  color: #92959e;
}

.new-messages {
  color: white;
  background-color: red;
  width: 20px;
  border-radius: 5px;
  text-align: center;
  float: right;
  margin-top: 10px;
}
</style>
