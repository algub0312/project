/**
 * Convert object keys from camelCase to snake_case
 * @param obj - The object to convert
 * @returns The converted object
 */
export function toSnakeCase(obj: any) {
  return Object.fromEntries(
    Object.entries(obj).map(([k, v]) => [
      k.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`),
      v,
    ]),
  )
}

/**
 * Convert object keys from snake_case to camelCase
 * @param obj - The object to convert
 * @returns The converted object
 */
export function toCamelCase(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map((v) => toCamelCase(v))
  }

  if (obj !== null && typeof obj === 'object') {
    return Object.entries(obj).reduce((acc, [key, val]) => {
      const camelKey = key.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
      acc[camelKey] = toCamelCase(val)
      return acc
    }, {} as any)
  }
  return obj
}
