import * as fabric from 'fabric'
import type { UnwrapRef } from 'vue'
import type { DeskDrawingData } from '@/types/deskDrawingData.ts'

const OFFICE_WIDTH_CM = 1200
const OFFICE_HEIGHT_CM = 750
const DESK_WIDTH_CM = 80
const DESK_LENGTH_CM = 150

function cmToPxX(cm: number, canvasWidthPx: number) {
  return (cm / OFFICE_WIDTH_CM) * canvasWidthPx
}

function cmToPxY(cm: number, canvasHeightPx: number) {
  return (cm / OFFICE_HEIGHT_CM) * canvasHeightPx
}

export function drawDesks(
  canvas: UnwrapRef<fabric.Canvas | null>,
  data: DeskDrawingData[],
  emitClick: (type: 'left' | 'right', deskId: number, ev?: MouseEvent) => void,
) {
  if (!canvas) {
    console.warn('No fabric canvas to draw desks on')
    return
  }

  console.log('Drawing desks on canvas...')
  console.log('Desks data:', data)
  canvas.clear()
  const cw = canvas.getWidth()
  const ch = canvas.getHeight()

  data.forEach((desk) => {
    const xPx = cmToPxX(desk.positionX, cw)
    const yPx = cmToPxY(desk.positionY, ch)

    const wPx =
      desk.orientation === 'vertical' ? cmToPxX(DESK_WIDTH_CM, cw) : cmToPxX(DESK_LENGTH_CM, cw)
    const hPx =
      desk.orientation === 'vertical' ? cmToPxY(DESK_LENGTH_CM, ch) : cmToPxY(DESK_WIDTH_CM, ch)

    const rect = new fabric.Rect({
      left: xPx,
      top: yPx,
      width: wPx,
      height: hPx,
      fill: desk.color,
      stroke: '#000',
      strokeWidth: 1,
      rx: 4,
      ry: 4,
      selectable: false,
    })

    const deskIdStr = desk.deskId.toString()
    const labelText = deskIdStr.length > 3 ? deskIdStr.slice(-3) : deskIdStr
    const label = new fabric.FabricText(labelText, {
      left: xPx + wPx / 2,
      top: yPx + hPx / 2,
      fontSize: 12,
      fill: '#fff',
    })

    const group = new fabric.Group([rect, label], { selectable: false }) as fabric.Group & {
      data: DeskDrawingData
    }
    group.data = desk

    group.on('mousedown', (opt) => {
      const ev = opt.e as MouseEvent | undefined
      if (!ev) return
      if (ev.button === 0) emitClick('left', desk.deskId, ev)
      if (ev.button === 2) {
        ev.preventDefault()
        emitClick('right', desk.deskId, ev)
      }
    })

    canvas.add(group)
  })

  canvas.renderAll()
}
