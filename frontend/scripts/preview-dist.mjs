// Lokalni server koji oponasa Vercel za dist/: prvo fajlovi, pa redirecti i rewrite-ovi
// iz vercel.json, a za sve ostalo 404.html sa statusom 404. `vite preview` ne cita
// vercel.json, pa se njime ne mogu proveriti ni redirecti ni pravi 404.
//
// Upotreba: node scripts/preview-dist.mjs [dist] [vercel.json] [port]
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'

const dist = path.resolve(process.argv[2] || 'dist')
const config = JSON.parse(fs.readFileSync(path.resolve(process.argv[3] || 'vercel.json'), 'utf-8'))
const port = Number(process.argv[4] || 4173)

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.ico': 'image/x-icon', '.txt': 'text/plain',
  '.webmanifest': 'application/manifest+json', '.xml': 'application/xml', '.woff2': 'font/woff2',
}

// "/steel/proizvod/:slug" -> RegExp sa imenovanim grupama; "(.*)" ostaje kao zahvat
function compile(source) {
  const names = []
  const pattern = source
    .replace(/[.+?^${}|[\]\\]/g, '\\$&')
    .replace(/:([a-zA-Z]+)\*/g, (_, n) => { names.push(n); return '(.*)' })
    .replace(/:([a-zA-Z]+)/g, (_, n) => { names.push(n); return '([^/]+)' })
    .replace(/\(\\\.\*\)/g, '(.*)')
  return { regex: new RegExp(`^${pattern}$`), names }
}

function fill(destination, names, match, query) {
  let out = destination
  names.forEach((n, i) => { out = out.replace(`:${n}`, match[i + 1] ?? '') })
  return out
}

function hasMatches(rule, query) {
  return (rule.has || []).every((h) => {
    if (h.type !== 'query') return false
    const value = query.get(h.key)
    if (value === null) return false
    return h.value === undefined || new RegExp(`^${h.value}$`).test(value)
  })
}

function readFile(urlPath) {
  const rel = decodeURIComponent(urlPath).replace(/^\/+/, '')
  const full = path.join(dist, rel)
  if (!full.startsWith(dist)) return null
  if (fs.existsSync(full) && fs.statSync(full).isFile()) return full
  const index = path.join(full, 'index.html')
  if (fs.existsSync(index)) return index
  return null
}

function send(res, status, file) {
  const type = TYPES[path.extname(file)] || 'application/octet-stream'
  res.writeHead(status, { 'content-type': type })
  fs.createReadStream(file).pipe(res)
}

http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${port}`)
  let pathname = url.pathname

  // trailingSlash: false -> /steel/ prelazi na /steel
  if (config.trailingSlash === false && pathname.length > 1 && pathname.endsWith('/')) {
    res.writeHead(308, { location: pathname.slice(0, -1) + url.search })
    return res.end()
  }

  for (const rule of config.redirects || []) {
    const { regex, names } = compile(rule.source)
    const match = pathname.match(regex)
    if (match && hasMatches(rule, url.searchParams)) {
      let dest = fill(rule.destination, names, match, url.searchParams)
      for (const h of rule.has || []) {
        dest = dest.replace(`:${h.key}`, url.searchParams.get(h.key) ?? '')
      }
      res.writeHead(rule.statusCode || 308, { location: dest })
      return res.end()
    }
  }

  const file = readFile(pathname)
  if (file) return send(res, 200, file)

  for (const rule of config.rewrites || []) {
    const { regex, names } = compile(rule.source)
    const match = pathname.match(regex)
    if (match && hasMatches(rule, url.searchParams)) {
      const dest = fill(rule.destination, names, match, url.searchParams)
      if (/^https?:/.test(dest)) {
        res.writeHead(502, { 'content-type': 'text/plain' })
        return res.end(`(spoljni rewrite, nije emuliran: ${dest})`)
      }
      const target = readFile(dest.split('?')[0])
      if (target) return send(res, 200, target)
      break
    }
  }

  const notFound = path.join(dist, '404.html')
  if (fs.existsSync(notFound)) return send(res, 404, notFound)
  res.writeHead(404, { 'content-type': 'text/plain' })
  res.end('404')
}).listen(port, () => console.log(`http://localhost:${port}  (dist: ${dist})`))
