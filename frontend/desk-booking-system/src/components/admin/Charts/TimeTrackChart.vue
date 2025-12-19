<script setup lang="ts">
import { plByTime } from '@/types/mockData'

const timeData = plByTime

// Calculate percentage based on maximum value
const calculatePercentage = (value: number) => {
  const maxValue = Math.max(...timeData.map((item) => item.value))
  return maxValue === 0 ? 0 : (value / maxValue) * 100
}
</script>

<template>
  <v-card class="pa-4">
    <v-card-title class="text-center">Daily Occupancy Rate</v-card-title>

    <!-- Chart Container -->
    <div class="chart-container pa-4">
      <!-- Y-axis labels -->
      <div class="y-axis pe-2">
        <div v-for="n in 6" :key="n" class="y-label">{{ 100 - (n - 1) * 20 }}%</div>
      </div>

      <!-- Bars Container -->
      <div class="bars-container">
        <div v-for="(item, index) in timeData" :key="index" class="bar-wrapper">
          <div class="bar-column">
            <v-sheet
              :height="`${calculatePercentage(item.value)}%`"
              width="40"
              color="#196ffa"
              class="bar"
            ></v-sheet>
          </div>
          <div class="x-label">{{ item.title }}</div>
        </div>
      </div>
    </div>
  </v-card>
</template>

<style scoped>
.chart-container {
  display: flex;
  height: 300px;
  position: relative;
  border-left: 1px solid #e0e0e0;
  border-bottom: 1px solid #e0e0e0;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: 50px;
}

.y-label {
  font-size: 12px;
  color: #666;
  height: 20px;
}

.bars-container {
  flex: 1;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  position: relative;
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.bar-column {
  height: 200px;
  display: flex;
  align-items: flex-end;
  margin: 0 4px;
}

.bar {
  transition: all 0.3s ease;
  border-radius: 4px 4px 0 0;
}

.bar:hover {
  background-color: #36d28c !important;
  cursor: pointer;
}

.x-label {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
}
</style>
