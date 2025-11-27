/**
 * Helper funkcija za kreiranje image URL-a
 * Podržava i Cloudinary (https://) i lokalne (/media/) URL-ove
 */
export function getImageUrl(imageUrl) {
  if (!imageUrl) return ''

  // Ako je već pun URL (http/https), vrati direktno (Cloudinary)
  if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
    return imageUrl
  }

  // Inače je lokalni URL, dodaj backend base URL
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://127.0.0.1:8000'
  return `${baseUrl}${imageUrl}`
}
