#!/usr/bin/env python3
"""
Test script za rate limiting funkcionalnost
"""
import requests
import time
from datetime import datetime

# Konfigurisano da koristi lokalni development server
BASE_URL = "http://localhost:8000/api"

def test_contact_rate_limiting():
    """
    Test kontakt forme - treba da dozvoli 3 zahteva na sat, 4. treba da blokira
    """
    print("=" * 60)
    print("TEST: Contact Form Rate Limiting (3 poruke/sat)")
    print("=" * 60)

    contact_data = {
        "name": "Test Korisnik",
        "email": "test@example.com",
        "phone": "0641234567",
        "message": "Test poruka"
    }

    for i in range(1, 5):
        response = requests.post(f"{BASE_URL}/contact/", json=contact_data)
        timestamp = datetime.now().strftime("%H:%M:%S")

        print(f"\n[{timestamp}] Zahtev #{i}:")
        print(f"  Status Code: {response.status_code}")

        if response.status_code == 429:
            print(f"  ✅ RATE LIMITED! (Očekivano)")
            try:
                data = response.json()
                print(f"  Poruka: {data.get('detail', 'N/A')}")
            except:
                print(f"  Response: {response.text[:100]}")
        elif response.status_code == 201:
            print(f"  ✅ Uspešno kreirana poruka")
        else:
            print(f"  ⚠️ Neočekivan status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")

        time.sleep(1)  # Pauza između zahteva

    print("\n" + "=" * 60)


def test_order_rate_limiting():
    """
    Test porudžbina - treba da dozvoli 10 zahteva na sat
    """
    print("=" * 60)
    print("TEST: Order Creation Rate Limiting (10 porudžbina/sat)")
    print("=" * 60)

    order_data = {
        "customer_name": "Test Kupac",
        "customer_phone": "0641234567",
        "customer_email": "test@example.com",
        "address": "Test Adresa 123",
        "city": "Beograd",
        "postal_code": "11000",
        "items": []  # Prazna porudžbina za test
    }

    # Testiramo samo prvih 12 zahteva (treba 11. i 12. da blokiraju)
    for i in range(1, 13):
        response = requests.post(f"{BASE_URL}/orders/", json=order_data)
        timestamp = datetime.now().strftime("%H:%M:%S")

        print(f"\n[{timestamp}] Zahtev #{i}:")
        print(f"  Status Code: {response.status_code}")

        if response.status_code == 429:
            print(f"  ✅ RATE LIMITED! (Očekivano posle 10. zahteva)")
            try:
                data = response.json()
                print(f"  Poruka: {data.get('detail', 'N/A')}")
            except:
                print(f"  Response: {response.text[:100]}")
        elif response.status_code in [201, 400]:
            # 201 = uspešno, 400 = validation error (očekivano jer su items prazni)
            if response.status_code == 201:
                print(f"  ✅ Uspešno kreirana porudžbina")
            else:
                print(f"  ⚠️ Validation error (očekivano - prazni items)")
        else:
            print(f"  ⚠️ Neočekivan status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")

        time.sleep(0.5)  # Pauza između zahteva


def main():
    print("\n🔒 RATE LIMITING TEST SCRIPT\n")

    # Proveri da li server radi
    try:
        response = requests.get(f"{BASE_URL}/products/", timeout=5)
        print(f"✅ Server je aktivan (Status: {response.status_code})\n")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server nije dostupan!")
        print(f"   Greška: {e}")
        print(f"\n💡 Pokreni development server sa:")
        print(f"   cd /home/teofilex/Projects/gvozdjara")
        print(f"   pipenv run python backend/manage.py runserver\n")
        return

    # Testovi
    test_contact_rate_limiting()

    print("\n\n⏳ Čekam 3 sekunde pre sledećeg testa...\n")
    time.sleep(3)

    test_order_rate_limiting()

    print("\n" + "=" * 60)
    print("TESTIRANJE ZAVRŠENO!")
    print("=" * 60)
    print("\n📝 Napomena:")
    print("   - Rate limit se resetuje nakon 1 sata")
    print("   - Za reset tokom testiranja, restartuj Django server")
    print("   - U produkciji, različite IP adrese imaju različite limite")
    print()


if __name__ == "__main__":
    main()
