package com.example.shop.model;

import java.math.BigDecimal;
import java.util.List;

/**
 * Entity representing a product.
 * Holds product name, price, stock quantity, and category information.
 */
public class Product {
    private Long id;
    private String name;
    private String description;
    private BigDecimal price;
    private int stockQuantity;
    private Category category;
    private List<String> tags;
    private boolean active;

    public Product(String name, BigDecimal price, Category category) {
        this.name = name;
        this.price = price;
        this.category = category;
        this.active = true;
    }

    public boolean isInStock() {
        return this.stockQuantity > 0;
    }

    public void reduceStock(int quantity) {
        if (quantity > this.stockQuantity) {
            throw new IllegalStateException("Insufficient stock");
        }
        this.stockQuantity -= quantity;
    }

    public BigDecimal getPriceWithTax(BigDecimal taxRate) {
        return this.price.multiply(BigDecimal.ONE.add(taxRate));
    }

    // getters and setters omitted for brevity
}
