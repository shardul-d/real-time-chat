<template>
  <div>
    <div class="left-panel">
      <User
        v-for="user in users"
        :key="user.userID"
        :user="user"
        :selected="selectedUser === user"
        @select="onSelectUser(user)"
      />
    </div>

    <MessagePanel
      v-if="selectedUser"
      :user="selectedUser"
      @input="onMessage"
      class="right-panel"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from "vue";
import socket from "../socket";
import User from "./User.vue";
import MessagePanel from "./MessagePanel.vue";

// ---------- Types ----------
interface Message {
  content: string;
  fromSelf: boolean;
}

interface UserType {
  userID: string;
  username: string;
  connected: boolean;
  self?: boolean;
  hasNewMessages?: boolean;
  messages: Message[];
}

// ---------- Reactive State ----------
const selectedUser = ref<UserType | null>(null);
const users = reactive<UserType[]>([]);

// ---------- Utility Functions ----------
function initReactiveProperties(user: UserType) {
  user.hasNewMessages = false;
  if (!user.messages) user.messages = [];
}

// ---------- Core Methods ----------
function onMessage(content: string) {
  if (!selectedUser.value) return;

  socket.emit("private message", {
    content,
    to: selectedUser.value.userID,
  });

  selectedUser.value.messages.push({
    content,
    fromSelf: true,
  });
}

function onSelectUser(user: UserType) {
  selectedUser.value = user;
  user.hasNewMessages = false;
}

// ---------- Socket Handlers ----------
onMounted(() => {
  socket.on("connect", () => {
    users.forEach((u) => {
      if (u.self) u.connected = true;
    });
  });

  socket.on("disconnect", () => {
    users.forEach((u) => {
      if (u.self) u.connected = false;
    });
  });

  socket.on("users", (incomingUsers: UserType[]) => {
    incomingUsers.forEach((user) => {
      // mark messages
      user.messages.forEach((msg) => {
        msg.fromSelf = msg.fromSelf ?? msg.fromSelf === undefined
          ? msg.fromSelf
          : false;
      });

      const existing = users.find((u) => u.userID === user.userID);
      if (existing) {
        existing.connected = user.connected;
        existing.messages = user.messages;
        return;
      }

      user.self = user.userID === socket.userID;
      initReactiveProperties(user);
      users.push(user);
    });

    // Sort: self first, then alphabetically
    users.sort((a, b) => {
      if (a.self) return -1;
      if (b.self) return 1;
      return a.username.localeCompare(b.username);
    });
  });

  socket.on("user connected", (user: UserType) => {
    const existing = users.find((u) => u.userID === user.userID);
    if (existing) {
      existing.connected = true;
      return;
    }
    initReactiveProperties(user);
    users.push(user);
  });

  socket.on("user disconnected", (id: string) => {
    const user = users.find((u) => u.userID === id);
    if (user) user.connected = false;
  });

  socket.on("private message", ({ content, from, to }: any) => {
    const fromSelf = socket.userID === from;
    const targetUser = users.find((u) => u.userID === (fromSelf ? to : from));
    if (targetUser) {
      targetUser.messages.push({ content, fromSelf });
      if (targetUser !== selectedUser.value) {
        targetUser.hasNewMessages = true;
      }
    }
  });
});

onUnmounted(() => {
  socket.off("connect");
  socket.off("disconnect");
  socket.off("users");
  socket.off("user connected");
  socket.off("user disconnected");
  socket.off("private message");
});
</script>

<style scoped>
.left-panel {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 260px;
  overflow-x: hidden;
  background-color: #3f0e40;
  color: white;
}

.right-panel {
  margin-left: 260px;
}
</style>
