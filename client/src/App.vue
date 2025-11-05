<template>
  <div id="app">
    <Login
      v-if="!credentialsEntered"
      @input="onLoginRequest"
    />
    <Chat v-else />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import Chat from "./components/Chat.vue";
import Login from "./components/Login.vue";
import socket from "./socket";
import axios from "axios";

// ---------- State ----------
const credentialsEntered = ref(false);

// ---------- Methods ----------
async function onLoginRequest(username: string, password: string) {
  try {
    await axios.post('/login', { "username": username, "password": password });
    credentialsEntered.value = true;
    // socket.auth = { username, password };
    // socket.connect();
  }
  catch (error) {
    console.log(error);
  }

}

// ---------- Lifecycle ----------
onMounted(async () => {
  try {
    const response = await axios.get('/check_authentication_status')

    if (response.status == 200) {
      credentialsEntered.value = true;
      socket.connect();
    }
  }
  catch (error) {
    console.warn('User not authenticated:', error)
  }

  socket.on("session", ({ sessionID, userID }: { sessionID: string; userID: string }) => {
    socket.auth = { sessionID };
    localStorage.setItem("sessionID", sessionID);
    (socket as any).userID = userID; // add dynamically to socket
  });

  socket.on("connect_error", (err: Error & { message?: string }) => {
    if (err.message === "invalid username") {
      credentialsEntered.value = false;
    }
  });
});

onUnmounted(() => {
  socket.off("connect_error");
});
</script>

<style>
body {
  margin: 0;
}

@font-face {
  font-family: Lato;
  src: "~/public/fonts/Lato-Regular.ttf";
}

#app {
  font-family: Lato, Arial, sans-serif;
  font-size: 14px;
}
</style>
