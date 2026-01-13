#!/bin/bash

# Jednostavan test za rate limiting - koristi curl

echo "=========================================="
echo "TEST: Contact Form Rate Limiting"
echo "Limit: 3 poruke po satu"
echo "=========================================="
echo ""

for i in {1..5}; do
    echo "Zahtev #$i:"
    curl -X POST http://localhost:8000/api/contact/ \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Test",
            "email": "test@test.com",
            "phone": "0641234567",
            "message": "Test poruka"
        }' \
        -w "\nHTTP Status: %{http_code}\n" \
        -s | head -c 200
    echo ""
    echo "---"
    sleep 1
done

echo ""
echo "=========================================="
echo "Ako vidiš HTTP Status: 429 - Rate limiting radi!"
echo "=========================================="
