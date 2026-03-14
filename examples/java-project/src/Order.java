package com.example.shop.model;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Entity representing an order.
 * Manages the list of purchased products, total amount, and order status.
 */
public class Order {
    private Long id;
    private User buyer;
    private List<OrderItem> items = new ArrayList<>();
    private OrderStatus status;
    private LocalDateTime orderedAt;
    private LocalDateTime shippedAt;

    public Order(User buyer) {
        this.buyer = buyer;
        this.status = OrderStatus.PENDING;
        this.orderedAt = LocalDateTime.now();
    }

    public void addItem(Product product, int quantity) {
        product.reduceStock(quantity);
        items.add(new OrderItem(product, quantity));
    }

    public BigDecimal getTotalAmount() {
        return items.stream()
            .map(OrderItem::getSubtotal)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public void ship() {
        if (this.status != OrderStatus.PAID) {
            throw new IllegalStateException("Order must be paid before shipping");
        }
        this.status = OrderStatus.SHIPPED;
        this.shippedAt = LocalDateTime.now();
    }

    public void cancel() {
        if (this.status == OrderStatus.SHIPPED) {
            throw new IllegalStateException("Cannot cancel shipped order");
        }
        this.status = OrderStatus.CANCELLED;
    }
}
