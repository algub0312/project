import { ref, onMounted, onBeforeUnmount, type Ref } from 'vue'
import * as fabric from 'fabric'

export function useFabricCanvas(canvasRef: Ref<HTMLCanvasElement | null | undefined>) {
  const fabricCanvas = ref<fabric.Canvas | null>(null)

  const buildCanvas = () => {
    if (!canvasRef.value) {
      console.warn('No canvas ref yet')
      return
    }

    const parentEl = document.getElementById('canvas-parent')
    if (!parentEl) {
      console.warn('#canvas-parent not found')
      return
    }

    const dimensions = parentEl.getBoundingClientRect()
    if (!dimensions.width || !dimensions.height) {
      console.warn('Parent has no size yet')
      return
    }

    console.log('Building fabric canvas with dimensions:', dimensions.width, dimensions.height)
    fabricCanvas.value = new fabric.Canvas(canvasRef.value, {
      width: dimensions.width,
      height: dimensions.height,
      selection: false,
    })
  }

  const disposeCanvas = () => {
    fabricCanvas.value?.dispose()
    fabricCanvas.value = null
  }

  onMounted(() => requestAnimationFrame(buildCanvas))

  onBeforeUnmount(disposeCanvas)

  return { fabricCanvas, buildCanvas, disposeCanvas }
}
