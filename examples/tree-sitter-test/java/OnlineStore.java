package com.example.store;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.stream.Collectors;

public class OnlineStore {
    private String storeName;
    private List<Product> catalog;
    private Map<String, Customer> customers;
    private List<Order> orders;
    private PaymentGateway paymentGateway;

    public OnlineStore(String storeName, PaymentGateway paymentGateway) {
        this.storeName = storeName;
        this.catalog = new ArrayList<>();
        this.customers = new HashMap<>();
        this.orders = new ArrayList<>();
        this.paymentGateway = paymentGateway;
    }

    public void addProduct(Product product) {
        catalog.add(product);
    }

    public void removeProduct(String productId) {
        catalog.removeIf(p -> p.getId().equals(productId));
    }

    public List<Product> searchProducts(String keyword) {
        return catalog.stream()
                .filter(p -> p.getName().toLowerCase().contains(keyword.toLowerCase())
                        || p.getDescription().toLowerCase().contains(keyword.toLowerCase()))
                .collect(Collectors.toList());
    }

    public List<Product> getProductsByCategory(String category) {
        return catalog.stream()
                .filter(p -> p.getCategory().equals(category))
                .collect(Collectors.toList());
    }

    public Customer registerCustomer(String email, String name, String address) {
        Customer customer = new Customer(email, name, address);
        customers.put(email, customer);
        return customer;
    }

    public Customer getCustomer(String email) {
        return customers.get(email);
    }

    public Order placeOrder(String customerEmail, List<CartItem> cartItems) {
        Customer customer = customers.get(customerEmail);
        if (customer == null) {
            throw new IllegalArgumentException("Customer not found: " + customerEmail);
        }

        double total = 0;
        for (CartItem item : cartItems) {
            Product product = findProductById(item.getProductId());
            if (product == null) {
                throw new IllegalArgumentException("Product not found: " + item.getProductId());
            }
            if (product.getStock() < item.getQuantity()) {
                throw new IllegalStateException("Insufficient stock for: " + product.getName());
            }
            total += product.getPrice() * item.getQuantity();
        }

        PaymentResult result = paymentGateway.charge(customer, total);
        if (!result.isSuccess()) {
            throw new RuntimeException("Payment failed: " + result.getErrorMessage());
        }

        for (CartItem item : cartItems) {
            Product product = findProductById(item.getProductId());
            product.reduceStock(item.getQuantity());
        }

        Order order = new Order(customer, cartItems, total, result.getTransactionId());
        orders.add(order);
        customer.addOrder(order);
        return order;
    }

    public Order cancelOrder(String orderId) {
        Order order = orders.stream()
                .filter(o -> o.getId().equals(orderId))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));

        paymentGateway.refund(order.getTransactionId(), order.getTotal());

        for (CartItem item : order.getItems()) {
            Product product = findProductById(item.getProductId());
            product.addStock(item.getQuantity());
        }

        order.setStatus(OrderStatus.CANCELLED);
        return order;
    }

    public List<Order> getOrderHistory(String customerEmail) {
        Customer customer = customers.get(customerEmail);
        if (customer == null) {
            return new ArrayList<>();
        }
        return customer.getOrders();
    }

    public Map<String, Double> getSalesReport() {
        Map<String, Double> report = new HashMap<>();
        for (Order order : orders) {
            if (order.getStatus() != OrderStatus.CANCELLED) {
                for (CartItem item : order.getItems()) {
                    Product product = findProductById(item.getProductId());
                    String category = product.getCategory();
                    report.merge(category, product.getPrice() * item.getQuantity(), Double::sum);
                }
            }
        }
        return report;
    }

    private Product findProductById(String productId) {
        return catalog.stream()
                .filter(p -> p.getId().equals(productId))
                .findFirst()
                .orElse(null);
    }

    public String getStoreName() {
        return storeName;
    }

    public int getTotalProducts() {
        return catalog.size();
    }

    public int getTotalCustomers() {
        return customers.size();
    }

    public int getTotalOrders() {
        return orders.size();
    }
}
