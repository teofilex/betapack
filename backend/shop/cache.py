"""
Kes odgovora liste proizvoda.

Koristi poseban alias 'products' (FileBasedCache u /tmp, bez novih servisa), a ne
'default': DRF throttling cuva brojace u 'default' kesu, pa bi pravi 'default' kes
ukljucio ogranicenje od 100 zahteva/sat po IP adresi (a iza Railway proxy-ja svi
posetioci bi delili isti brojac).

Poništavanje ide preko "verzije": kljuc kesa sadrzi verziju, a svaka izmena
proizvoda, varijante, slike ili kategorije podigne verziju. Odgovor izracunat dok
se izmena desavala ostaje pod starom verzijom i nikad se ne cita.
"""
import time

from django.core.cache import caches
from django.db import transaction

CACHE_ALIAS = 'products'
VERSION_KEY = 'products:version'
LIST_TTL = 60 * 5  # sigurnosna granica; stvarno poništavanje radi verzija
CACHEABLE_STORES = (None, 'steel', 'ambalaza')


def _cache():
    return caches[CACHE_ALIAS]


def current_version():
    cache = _cache()
    version = cache.get(VERSION_KEY)
    if version is None:
        version = time.time_ns()
        cache.add(VERSION_KEY, version, timeout=None)
        version = cache.get(VERSION_KEY, version)
    return version


def list_key(store):
    return f'products:list:{store or "all"}:{current_version()}'


def bump_version():
    _cache().set(VERSION_KEY, time.time_ns(), timeout=None)


def invalidate_products_cache(**kwargs):
    """Signal handler: poništava kes tek kad je izmena u bazi potvrđena."""
    transaction.on_commit(bump_version)
