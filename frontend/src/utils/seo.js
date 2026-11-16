// Glavna adresa sajta je www, a putanje su bez kose crte na kraju.
// Canonical i og:url moraju biti pravi URL strane, nikad adresa koja se redirectuje.
export const SITE_URL = 'https://www.betapack.co.rs'
export const DEFAULT_OG_IMAGE = `${SITE_URL}/Betapack-hero-image-optimized.jpg`

export const absoluteUrl = (path = '/') => `${SITE_URL}${path.startsWith('/') ? path : `/${path}`}`

// Sastavlja title, description, canonical, Open Graph i Twitter tagove za jednu stranu.
// Koristi se kao useHead(() => buildHead({...})), pa vrednosti mogu biti reaktivne.
export function buildHead({ title, description, path = '/', image = DEFAULT_OG_IMAGE, imageAlt, type = 'website' }) {
  const url = absoluteUrl(path)
  const alt = imageAlt || title

  return {
    title,
    meta: [
      { name: 'description', content: description },
      // Open Graph
      { property: 'og:site_name', content: 'BetaPack' },
      { property: 'og:title', content: title },
      { property: 'og:description', content: description },
      { property: 'og:image', content: image },
      { property: 'og:image:alt', content: alt },
      { property: 'og:url', content: url },
      { property: 'og:type', content: type },
      { property: 'og:locale', content: 'sr_RS' },
      // Twitter Card
      { name: 'twitter:card', content: 'summary_large_image' },
      { name: 'twitter:title', content: title },
      { name: 'twitter:description', content: description },
      { name: 'twitter:image', content: image },
      { name: 'twitter:image:alt', content: alt }
    ],
    link: [
      { rel: 'canonical', href: url }
    ]
  }
}
