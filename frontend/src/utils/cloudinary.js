// Slike proizvoda su na Cloudinary-ju u originalnoj velicini. Transformacije se traze
// samo preko URL-a (nista se ne menja na Cloudinary-ju): f_auto bira WebP/AVIF po
// pregledacu, q_auto kvalitet, w_N + c_limit smanjuje na trazenu sirinu (nikad ne
// uvecava). Lokalni (/media/) i tudji URL-ovi ostaju nepromenjeni.
const UPLOAD_MARKER = '/image/upload/'

const isCloudinary = (url) => typeof url === 'string' && url.includes('res.cloudinary.com') && url.includes(UPLOAD_MARKER)

export function cloudinaryUrl(url, { width, format = 'auto' } = {}) {
  if (!isCloudinary(url)) return url
  const transforms = [`f_${format}`, 'q_auto']
  if (width) transforms.push(`w_${width}`, 'c_limit')
  return url.replace(UPLOAD_MARKER, `${UPLOAD_MARKER}${transforms.join(',')}/`)
}

// "url1 320w, url2 480w, ..." ili '' ako URL nije sa Cloudinary-ja
export function cloudinarySrcset(url, widths) {
  if (!isCloudinary(url)) return ''
  return widths.map((width) => `${cloudinaryUrl(url, { width })} ${width}w`).join(', ')
}
