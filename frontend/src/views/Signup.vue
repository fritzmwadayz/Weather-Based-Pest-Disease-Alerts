<template>
  <div>
    <h1>Sign Up</h1>
    <form @submit.prevent="signup">
      <input v-model="username" type="text" placeholder="Username" required />
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <button type="submit">Sign Up</button>
    </form>
    <router-link to="/login">Already have an account? Login</router-link>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api';

const username = ref('');
const email = ref('');
const password = ref('');
const router = useRouter();

const signup = async () => {
  try {
    const response = await apiClient.post('/signup', {
      username: username.value,
      email: email.value,
      password: password.value,
    });

    if (response.data.success) {
      alert('Account created successfully! Please log in.');
      router.push('/login');
    } else {
      alert(response.data.message);
    }
  } catch (error) {
    console.error('Signup failed:', error);
    alert('Signup failed. Please try again.');
  }
};
</script>