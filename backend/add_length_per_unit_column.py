#!/usr/bin/env python
"""
Skripta za dodavanje length_per_unit kolone direktno u SQLite bazu
Pokrenite: python add_length_per_unit_column.py
"""

import sqlite3
import os

# Putanja do baze
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

if not os.path.exists(db_path):
    print(f"Baza {db_path} ne postoji!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Proveri da li kolona već postoji
    cursor.execute("PRAGMA table_info(shop_product)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'length_per_unit' in columns:
        print("Kolona length_per_unit već postoji!")
    else:
        # Dodaj kolonu
        cursor.execute("""
            ALTER TABLE shop_product 
            ADD COLUMN length_per_unit DECIMAL(10, 2) DEFAULT 6.0
        """)
        
        # Ažuriraj postojeće proizvode sa default vrednošću
        cursor.execute("""
            UPDATE shop_product 
            SET length_per_unit = 6.0 
            WHERE length_per_unit IS NULL
        """)
        
        conn.commit()
        print("✓ Kolona length_per_unit uspešno dodata!")
        print("✓ Svi postojeći proizvodi su ažurirani sa default vrednošću 6.0")
        
except sqlite3.Error as e:
    print(f"Greška: {e}")
    conn.rollback()
finally:
    conn.close()



