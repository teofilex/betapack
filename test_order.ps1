# Test Order Request - First get products, then create order
$baseUrl = "http://localhost:8000/api"

# Step 1: Get products to find valid product IDs
Write-Host "Step 1: Fetching products..." -ForegroundColor Cyan
try {
    $productsResponse = Invoke-WebRequest -Uri "$baseUrl/products/" -Method GET
    $products = $productsResponse.Content | ConvertFrom-Json
    
    if ($products.Count -eq 0) {
        Write-Host "❌ No products found in database. Please add products first." -ForegroundColor Red
        exit
    }
    
    Write-Host "Found $($products.Count) products" -ForegroundColor Green
    Write-Host "First 3 products:" -ForegroundColor Yellow
    $products | Select-Object -First 3 | ForEach-Object {
        Write-Host "  ID: $($_.id), Name: $($_.name), Price: $($_.current_price) RSD" -ForegroundColor Gray
    }
    
    # Use first product
    $firstProduct = $products[0]
    if ($products.Count -gt 1) {
        $secondProduct = $products[1]
    } else {
        $secondProduct = $products[0]  # Use first if only one product
    }
    
    Write-Host "`nStep 2: Creating order with products ID $($firstProduct.id) and $($secondProduct.id)..." -ForegroundColor Cyan
    
    # Step 2: Create order
    $orderData = @{
        customer_name = "Marko Petrovic"
        customer_phone = "0612345678"
        customer_email = "marko.petrovic@example.com"
        delivery_address = "Bulevar Kralja Aleksandra 123, Beograd"
        notes = "Molim hitnu dostavu do 15h"
        items = @(
            @{
                product_id = $firstProduct.id
                quantity = 2
            },
            @{
                product_id = $secondProduct.id
                quantity = 1
            }
        )
    }
    
    $jsonBody = $orderData | ConvertTo-Json -Depth 10 -Compress
    
    $headers = @{
        "Content-Type" = "application/json; charset=utf-8"
    }
    
    $url = "$baseUrl/orders/"
    
    Write-Host "Request body:" -ForegroundColor Yellow
    Write-Host $jsonBody -ForegroundColor Gray
    
    $response = Invoke-WebRequest -Uri $url -Method POST -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($jsonBody))
    
    Write-Host "`nStatus Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Yellow
    $order = $response.Content | ConvertFrom-Json
    $order | ConvertTo-Json -Depth 10
    
    if ($response.StatusCode -eq 201) {
        Write-Host "`n✅ Order successfully created!" -ForegroundColor Green
        Write-Host "Order ID: $($order.id)" -ForegroundColor Cyan
        Write-Host "Customer: $($order.customer_name)" -ForegroundColor Cyan
        Write-Host "Total Amount: $($order.total_amount) RSD" -ForegroundColor Cyan
        Write-Host "Status: $($order.status)" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "`n❌ Error occurred:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody" -ForegroundColor Yellow
    }
}
