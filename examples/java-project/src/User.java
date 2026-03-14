package com.example.shop.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Entity representing a user account.
 * Holds authentication credentials, profile, and purchase history.
 */
public class User {
    private Long id;
    private String email;
    private String passwordHash;
    private String displayName;
    private LocalDateTime createdAt;
    private LocalDateTime lastLoginAt;
    private List<Order> orderHistory = new ArrayList<>();

    public User(String email, String displayName) {
        this.email = email;
        this.displayName = displayName;
        this.createdAt = LocalDateTime.now();
    }

    public boolean verifyPassword(String rawPassword) {
        return PasswordUtil.verify(rawPassword, this.passwordHash);
    }

    public void addOrder(Order order) {
        this.orderHistory.add(order);
    }

    public int getTotalPurchaseCount() {
        return this.orderHistory.size();
    }

    // getters and setters omitted for brevity
}
