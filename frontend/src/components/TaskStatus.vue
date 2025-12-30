<template>
  <div>
    <h3>Task Status</h3>
    <p v-if="loading">Checking task status...</p>
    <p v-else-if="status">Status: {{ status }}</p>
    <p v-if="result">Result: {{ result }}</p>
    <button v-if="!isCompleted" @click="checkTaskStatus">Refresh</button>
  </div>
</template>

<script>
export default {
  props: ["taskId"],
  data() {
    return {
      status: null,
      result: null,
      loading: false,
      intervalId: null, // Store interval for auto-refresh
    };
  },
  computed: {
    isCompleted() {
      return this.status === "SUCCESS" || this.status === "FAILURE";
    }
  },
  methods: {
    async checkTaskStatus() {
      this.loading = true;
      try {
        const response = await fetch(`/task-status/${this.taskId}`);
        const data = await response.json();
        this.status = data.status;
        this.result = data.result;

        // Stop auto-refresh if task is completed
        if (this.isCompleted) {
          clearInterval(this.intervalId);
        }
      } catch (error) {
        console.error("Error fetching task status:", error);
      }
      this.loading = false;
    },
    startAutoRefresh() {
      this.checkTaskStatus(); // Fetch status immediately
      this.intervalId = setInterval(() => {
        if (!this.isCompleted) {
          this.checkTaskStatus();
        }
      }, 3000); // Check every 3 seconds
    }
  },
  mounted() {
    this.startAutoRefresh();
  },
  beforeUnmount() {
    clearInterval(this.intervalId); // Cleanup when component is destroyed
  }
};
</script>

