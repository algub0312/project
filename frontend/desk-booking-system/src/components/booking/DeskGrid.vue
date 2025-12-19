<script setup lang="ts">
import { ref, watch } from 'vue'
import { useFabricCanvas } from '@/composables/canvas/useFabricCanvas'
import { drawDesks } from '@/composables/canvas/utils/drawDesks'
import type { DeskDrawingData } from '@/types/deskDrawingData.ts'

const props = defineProps<{
  drawingData: DeskDrawingData[]
}>()

const emits = defineEmits<{
  (e: 'left', deskId: number): void
  (e: 'right', deskId: number, ev: MouseEvent): void
}>()

const canvasEl = ref<HTMLCanvasElement | null>()
const { fabricCanvas } = useFabricCanvas(canvasEl)

const emitClick = (type: 'left' | 'right', deskId: number, ev?: MouseEvent) => {
  if (type === 'left') emits('left', deskId)
  if (type === 'right' && ev) emits('right', deskId, ev)
}

// initial draw when canvas is ready
watch(fabricCanvas, (newCanvas) => {
  if (newCanvas) {
    drawDesks(newCanvas, props.drawingData, emitClick)
  }
})

// redraw whenever desks change or canvas is ready
watch(
  () => props.drawingData,
  () => {
    if (!fabricCanvas.value) {
      console.warn('Fabric canvas not initialized yet')
      return
    }

    drawDesks(fabricCanvas.value, props.drawingData, emitClick)
  },
  { deep: true, immediate: true },
)
</script>

<template>
  <div id="canvas-parent" class="desk-canvas-wrapper">
    <canvas ref="canvasEl"></canvas>
  </div>
</template>

<style scoped>
.desk-canvas-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 1;
}
canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
