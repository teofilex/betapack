/** Način prodaje i cene za ambalažu — po varijanti. Gvožđara koristi useSellingMode.js. */

export function getAmbalazaSellingMode(product, variant = null) {
  if (variant?.selling_mode) return variant.selling_mode
  if (product?.selling_mode) return product.selling_mode
  return 'piece'
}

export function getAmbalazaOnRequestUnit(product, variant = null) {
  if (variant?.on_request_unit) return variant.on_request_unit
  if (product?.on_request_unit) return product.on_request_unit
  return 'piece'
}

export function isAmbalazaOnRequest(product, variant = null) {
  return getAmbalazaSellingMode(product, variant) === 'on_request'
}

export function isAmbalazaPackageMode(product, variant = null) {
  const mode = getAmbalazaSellingMode(product, variant)
  if (mode === 'on_request') {
    return getAmbalazaOnRequestUnit(product, variant) === 'package'
  }
  return mode === 'package'
}

export function isAmbalazaWeightMode(product, variant = null) {
  const mode = getAmbalazaSellingMode(product, variant)
  if (mode === 'on_request') {
    return getAmbalazaOnRequestUnit(product, variant) === 'weight'
  }
  return mode === 'weight'
}

export function getAmbalazaPackageSize(product, variant = null) {
  const mode = getAmbalazaSellingMode(product, variant)
  if (mode === 'on_request') {
    if (getAmbalazaOnRequestUnit(product, variant) === 'package') {
      return parseInt(variant?.package_size ?? product?.package_size, 10) || 1
    }
    return 1
  }
  if (variant?.selling_mode === 'package') {
    return parseInt(variant.package_size, 10) || 1
  }
  return parseInt(product?.package_size, 10) || 1
}

export function getAmbalazaQuantityStep(product, variant = null) {
  if (isAmbalazaPackageMode(product, variant)) {
    return getAmbalazaPackageSize(product, variant)
  }
  return 1
}

export function getAmbalazaMinQuantity(product, variant = null) {
  return getAmbalazaQuantityStep(product, variant)
}

export function getAmbalazaDefaultQuantity(product, variant = null) {
  return getAmbalazaMinQuantity(product, variant)
}

export function isAmbalazaValidQuantity(product, quantity, variant = null) {
  if (isAmbalazaPackageMode(product, variant)) {
    const pkg = getAmbalazaPackageSize(product, variant)
    return quantity > 0 && quantity % pkg === 0
  }
  return quantity >= 1
}

export function getAmbalazaDisplayPrice(product, variant = null) {
  if (isAmbalazaOnRequest(product, variant)) return null
  if (variant) {
    const price = variant.current_price ?? variant.price
    if (price != null) return parseFloat(price)
  }
  const price = product?.current_price ?? product?.min_price ?? product?.price
  return price != null ? parseFloat(price) : null
}

export function formatAmbalazaPriceLabel(product, variant, formatPrice) {
  if (isAmbalazaOnRequest(product, variant)) return 'Cena na upit'
  const mode = getAmbalazaSellingMode(product, variant)
  const price = getAmbalazaDisplayPrice(product, variant)
  if (price == null) return 'Cena na upit'
  if (mode === 'package') return `${formatPrice(price)} / kom.`
  if (mode === 'weight') return `${formatPrice(price)} / kg`
  return formatPrice(price)
}

export function getAmbalazaSellingNote(product, variant = null) {
  const mode = getAmbalazaSellingMode(product, variant)
  if (mode === 'on_request') {
    const unit = getAmbalazaOnRequestUnit(product, variant)
    if (unit === 'package') {
      const pkg = getAmbalazaPackageSize(product, variant)
      return `Prodaja na upit — po pakovanju (${pkg} kom.)`
    }
    if (unit === 'weight') return 'Prodaja na upit — po kilogramu'
    return 'Prodaja na upit — po komadu'
  }
  if (mode === 'package') {
    const pkg = getAmbalazaPackageSize(product, variant)
    return `Prodaje se po pakovanju (${pkg} kom.)`
  }
  if (mode === 'weight') return 'Prodaje se po kilogramu'
  return 'Prodaje se po komadu'
}

export function getAmbalazaPackageNote(product, variant = null) {
  if (!isAmbalazaPackageMode(product, variant)) return null
  const pkg = getAmbalazaPackageSize(product, variant)
  return `Pakovanje: ${pkg} komada`
}

export function getAmbalazaLineTotal(product, variant, quantity, formatPrice) {
  const unitPrice = getAmbalazaDisplayPrice(product, variant)
  if (unitPrice == null) return null
  return formatPrice(unitPrice * quantity)
}

export function getAmbalazaMinQuantityFromItem(item) {
  if (item?.selling_mode === 'on_request' && item?.on_request_unit === 'package') {
    return parseInt(item.package_size, 10) || 1
  }
  if (item?.selling_mode === 'package') {
    return parseInt(item.package_size, 10) || 1
  }
  return 1
}

export function getAmbalazaQuantityStepFromItem(item) {
  return getAmbalazaMinQuantityFromItem(item)
}

export function isAmbalazaValidQuantityFromItem(item, quantity) {
  if (item?.selling_mode === 'on_request' && item?.on_request_unit === 'package') {
    const pkg = parseInt(item.package_size, 10) || 1
    return quantity > 0 && quantity % pkg === 0
  }
  if (item?.selling_mode === 'package') {
    const pkg = parseInt(item.package_size, 10) || 1
    return quantity > 0 && quantity % pkg === 0
  }
  return quantity >= 1
}
