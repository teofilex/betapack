export const STORES = {
  steel: {
    id: 'steel',
    path: '/steel',
    label: 'Beta Pack — Kovano gvožđe',
    shortLabel: 'Kovano gvožđe',
    tagline: 'Kovano gvožđe i bravarski materijali',
    description: 'Profili, kutije, firiketi i ukrasni elementi za ograde, kapije i gelendere.',
    heroImage: '/Betapack-hero-image-optimized.jpg',
    heroTitle: 'Kovano gvožđe i bravarski proizvodi',
    heroSubtitle: 'Širok asortiman kvalitetnih proizvoda - profili, cevi, čelik u traci, ukrasni elementi i dodatna oprema za bravariju',
    footerDescription: 'Prodaja bravarskih materijala i elemenata od kovanog gvožđa — kapije, ograde, gelenderi, dekorativni elementi i metalne konstrukcije.',
    footerTagline: 'Kvalitetni materijali, brza isporuka i pouzdana saradnja.',
    accentColor: '#1976d2',
    accentColorDark: '#0d47a1',
    gradientFrom: '#1e88e5',
    gradientTo: '#0d47a1',
    glow: 'rgba(25, 118, 210, 0.45)',
    features: ['Profili i kutije', 'Firiketi i šipke', 'Ukrasni elementi'],
    seoTitle: 'Kovano Gvožđe Beograd | Beta Pack',
    seoDescription: 'Beta Pack — prodaja bravarskih materijala od kovanog gvožđa u Beogradu.',
    aboutSeoTitle: 'O nama | Kovano gvožđe i bravarski materijal | Beta Pack',
    aboutSeoDescription: 'Beta Pack iz Batajnice prodaje bravarski materijal i elemente od kovanog gvožđa za kapije, ograde, gelendere i metalne konstrukcije.',
    contactSeoTitle: 'Kontakt | Kovano gvožđe Beograd | Beta Pack',
    contactSeoDescription: 'Kontaktirajte Beta Pack za bravarski materijal i kovano gvožđe. Pukovnika Milenka Pavlovića 159 A, Batajnica (Zemun), tel. 065/330 02 42.',
    heroContactButton: 'Pošalji upit',
  },
  ambalaza: {
    id: 'ambalaza',
    path: '/ambalaza',
    label: 'Beta Pack Ambalaža',
    shortLabel: 'Ambalaža',
    tagline: 'Ambalaža za hranu i ugostiteljstvo',
    description: 'PET, PP, papir, karton, alu, stiropor, folije i dodatna oprema — za restorane, kafiće, pekare i dostavu hrane.',
    heroImage: '/AmbalazaHeroImage.jpeg',
    heroTitle: 'Ambalaža za hranu',
    heroSubtitle: 'Beta Pack nudi širok izbor ambalaže za restorane, kafiće, pekare, poslastičarnice, mesare, fast food objekte, maloprodaju i dostavu hrane.',
    heroTags: ['PET', 'PP', 'papir', 'karton', 'alu', 'stiropor', 'folije', 'dodatna oprema'],
    heroTagline: 'Brza isporuka. Pouzdana saradnja. Širok asortiman.',
    heroOfferNote: 'Za veće količine i redovne kupce pripremamo posebne ponude.',
    heroCatalogButton: 'Pogledaj ponudu',
    heroContactButton: 'Pošalji upit',
    footerDescription: 'Širok izbor ambalaže za restorane, kafiće, pekare, poslastičarnice, mesare, fast food objekte, maloprodaju i dostavu hrane.',
    footerTagline: 'PET, PP, papir, karton, alu, stiropor, folije i dodatna oprema — na jednom mestu.',
    accentColor: '#1976d2',
    accentColorDark: '#0d47a1',
    gradientFrom: '#1e88e5',
    gradientTo: '#0d47a1',
    glow: 'rgba(25, 118, 210, 0.45)',
    features: ['Posude i ambalaža', 'Folije i kese', 'Prodaja na pakovanje'],
    seoTitle: 'Ambalaža za hranu Beograd | BetaPack Ambalaža',
    seoDescription: 'Beta Pack nudi širok izbor ambalaže za restorane, kafiće, pekare, poslastičarnice, mesare, fast food objekte, maloprodaju i dostavu hrane.',
    aboutSeoTitle: 'O nama | Ambalaža za hranu i ugostiteljstvo | Beta Pack',
    aboutSeoDescription: 'Beta Pack nudi ambalažu za restorane, kafiće, pekare, poslastičarnice, mesare i dostavu hrane: PET, PP, papir, karton, alu, stiropor i folije.',
    contactSeoTitle: 'Kontakt | Ambalaža za hranu Beograd | Beta Pack',
    contactSeoDescription: 'Pošaljite upit za ambalažu za hranu i ugostiteljstvo. Beta Pack, Pukovnika Milenka Pavlovića 159 A, Batajnica (Zemun), tel. 065/330 02 42.',
  },
}

export const STORE_LIST = Object.values(STORES)

export function getStoreById(id) {
  return STORES[id] || STORES.steel
}

export function getStoreFromPath(path) {
  if (path.startsWith('/ambalaza')) return STORES.ambalaza
  if (path.startsWith('/steel')) return STORES.steel
  return null
}
