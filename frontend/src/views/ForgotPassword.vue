<template>
  <div>
    <h1>Forgot Password</h1>
    <form @submit.prevent="forgotPassword">
      <input v-model="email" type="email" placeholder="Email" required />
      <button type="submit">Send Reset Email</button>
    </form>
    <router-link to="/login">Back to Login</router-link>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '@/api';

const email = ref('');

const forgotPassword = async () => {
  try {
    const response = await apiClient.post('/forgot-password', {
      email: email.value,
    });

    if (response.data.success) {
      alert('Reset email sent. Check your inbox.');
    } else {
      alert(response.data.message);
    }
  } catch (error) {
    console.error('Failed to send reset email:', error);
    alert('Failed to send reset email. Please try again.');
  }
};
</script>