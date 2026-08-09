export function formatApiError(error, fallback = 'Došlo je do greške.') {
  const data = error?.response?.data

  if (!data) {
    return error?.message || fallback
  }

  if (typeof data === 'string') {
    return data
  }

  if (data.detail) {
    return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
  }

  if (typeof data === 'object') {
    return Object.entries(data)
      .map(([key, value]) => {
        const label = Array.isArray(value) ? value.join(', ') : String(value)
        return `${key}: ${label}`
      })
      .join(' | ')
  }

  return fallback
}
