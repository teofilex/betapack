import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', {
    state: () => {
        // Load cart from localStorage and validate items
        const savedCart = JSON.parse(localStorage.getItem('cart') || '[]')

        // Filter out items without current_price (old/invalid data)
        const validItems = savedCart.filter(item => {
            return item.current_price !== undefined && item.current_price !== null
        })

        // If we filtered out items, save the cleaned cart
        if (validItems.length !== savedCart.length) {
            localStorage.setItem('cart', JSON.stringify(validItems))
        }

        return {
            items: validItems
        }
    },

    getters: {
        itemCount: (state) => {
            return state.items.reduce((sum, i) => sum + i.quantity, 0)
        },

        total: (state) => {
            return state.items.reduce((sum, item) => {
                // Use stored current_price (which should already include variant price if applicable)
                const price = parseFloat(item.current_price) || 0
                return sum + (price * item.quantity)
            }, 0)
        },
        
        // Helper to get item price (with variant if applicable)
        getItemPrice: (state) => (item) => {
            // If item has a selectedVariant with final_price, use that
            if (item.selectedVariant && item.selectedVariant.final_price) {
                return parseFloat(item.selectedVariant.final_price)
            }
            // Otherwise use stored current_price
            return parseFloat(item.current_price) || 0
        },

        isInCart: (state) => (productId, variantId = null) => {
            if (variantId) {
                const cartId = `${productId}-${variantId}`
                return state.items.some(i => i.cartId === cartId)
            }
            // If no variant specified, check if ANY variant of this product is in cart
            return state.items.some(i => i.id === productId)
        },

        getCartItem: (state) => (productId, variantId = null) => {
            if (variantId) {
                const cartId = `${productId}-${variantId}`
                return state.items.find(i => i.cartId === cartId)
            }
            // If no variant specified, return first item with this product id
            return state.items.find(i => i.id === productId)
        }
    },

    actions: {
        save() {
            localStorage.setItem('cart', JSON.stringify(this.items))
        },

        load() {
            const saved = localStorage.getItem('cart')
            if (saved) {
                this.items = JSON.parse(saved)
            }
        },

        add(product, quantity = 1) {
            const cartId = product.selectedVariant
                ? `${product.id}-${product.selectedVariant.id}`
                : product.id

            const found = this.items.find(i => i.cartId === cartId)

            // Calculate the correct price: use variant's final_price if variant exists, otherwise use product's current_price
            let itemPrice = product.current_price
            if (product.selectedVariant && product.selectedVariant.final_price) {
                itemPrice = parseFloat(product.selectedVariant.final_price)
            } else {
                itemPrice = parseFloat(product.current_price) || 0
            }

            if (found) {
                found.quantity += quantity
                // Update price in case it changed
                found.current_price = itemPrice
            } else {
                this.items.push({
                    cartId: cartId,
                    id: product.id,
                    name: product.name,
                    current_price: itemPrice,
                    images: product.images || [],
                    category_name: product.category_name,
                    selectedVariant: product.selectedVariant || null,
                    quantity: quantity
                })
            }

            this.save()
        },

        updateQuantity(itemId, newQuantity) {
            const item = this.items.find(i => i.cartId === itemId || i.id === itemId)
            if (item && newQuantity >= 1) {
                item.quantity = newQuantity
                this.save()
            }
        },

        remove(itemId) {
            this.items = this.items.filter(i => i.cartId !== itemId && i.id !== itemId)
            this.save()
        },

        clear() {
            this.items = []
            this.save()
        }
    }
})
