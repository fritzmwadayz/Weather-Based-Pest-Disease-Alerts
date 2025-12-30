<template>
  <div>
    <h1>Reset Password</h1>
    <form @submit.prevent="resetPassword">
      <input v-model="token" type="text" placeholder="Reset Token" required />
      <input v-model="newPassword" type="password" placeholder="New Password" required />
      <button type="submit">Reset Password</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api';

const token = ref('');
const newPassword = ref('');
const router = useRouter();

const resetPassword = async () => {
  try {
    const response = await apiClient.post('/reset-password', {
      token: token.value,
      new_password: newPassword.value,
    });

    if (response.data.success) {
      alert('Password reset successful!');
      router.push('/login');
    } else {
      alert(response.data.message);
    }
  } catch (error) {
    console.error('Failed to reset password:', error);
    alert('Failed to reset password. Please try again.');
  }
};
</script>