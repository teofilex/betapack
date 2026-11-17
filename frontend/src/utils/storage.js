// localStorage postoji samo u browseru. Pri prerenderu (Node) ga nema, a u privatnom
// modu nekih browsera pristup baca gresku; u oba slucaja se ponasa kao prazan.
export const storage = {
  get(key) {
    try {
      return typeof localStorage === 'undefined' ? null : localStorage.getItem(key)
    } catch {
      return null
    }
  },
  set(key, value) {
    try {
      if (typeof localStorage !== 'undefined') localStorage.setItem(key, value)
    } catch {
      /* puna ili zabranjena memorija: ignorisi */
    }
  },
  remove(key) {
    try {
      if (typeof localStorage !== 'undefined') localStorage.removeItem(key)
    } catch {
      /* ignorisi */
    }
  },
}
