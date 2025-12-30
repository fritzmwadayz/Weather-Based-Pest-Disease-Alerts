<template>
  <BaseLayout :username="username">
    <h2>Admin Dashboard</h2>
    <div class="row">
      <div class="col-md-4">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <h5 class="card-title">Total Users</h5>
            <p class="card-text">{{ totalUsers }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-success text-white">
          <div class="card-body">
            <h5 class="card-title">Predictions Made</h5>
            <p class="card-text">{{ totalPredictions }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card bg-warning text-dark">
          <div class="card-body">
            <h5 class="card-title">Active Farms</h5>
            <p class="card-text">{{ activeFarms }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-4">
      <canvas id="predictionChart"></canvas>
    </div>
  </BaseLayout>
</template>

<script>
import BaseLayout from './Base.vue';
import LineChartComponent from '@/components/LineChart.vue';

export default {
  name: 'AdminDashboard',
  components: {
    BaseLayout,
  },
  data() {
    return {
      username: 'Admin', // Replace with dynamic username if needed
      totalUsers: 'Loading...',
      totalPredictions: 'Loading...',
      activeFarms: 'Loading...',
      predictionDates: [],
      predictionCounts: [],
    };
  },
  async mounted() {
    // Fetch data from the backend
    const response = await fetch('/api/admin_data');
    const data = await response.json();

    this.totalUsers = data.total_users;
    this.totalPredictions = data.total_predictions;
    this.activeFarms = data.active_farms;
    this.predictionDates = data.prediction_dates;
    this.predictionCounts = data.prediction_counts;

    // Render Chart
    const ctx = document.getElementById('predictionChart').getContext('2d');
    new LineChartComponent(ctx, {
      type: 'line',
      data: {
        labels: this.predictionDates,
        datasets: [
          {
            label: 'Predictions Over Time',
            data: this.predictionCounts,
            borderColor: 'blue',
            fill: false,
          },
        ],
      },
    });
  },
};
</script>

<style scoped>
/* Add your styles here */
</style>

