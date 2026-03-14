package com.example.shop.service;

import com.example.shop.model.Order;
import java.math.BigDecimal;

/**
 * Service responsible for payment processing.
 * Handles credit card charges, refunds, and payment history management.
 */
public class PaymentService {
    private final PaymentGateway gateway;
    private final PaymentRepository paymentRepository;

    public PaymentService(PaymentGateway gateway, PaymentRepository paymentRepository) {
        this.gateway = gateway;
        this.paymentRepository = paymentRepository;
    }

    public PaymentResult charge(Order order, CreditCard card) {
        BigDecimal amount = order.getTotalAmount();

        PaymentResult result = gateway.charge(card.getToken(), amount);
        if (!result.isSuccess()) {
            throw new PaymentException("Payment failed: " + result.getErrorMessage());
        }

        Payment payment = new Payment(order.getId(), amount, result.getTransactionId());
        paymentRepository.save(payment);

        order.markAsPaid();
        return result;
    }

    public void refund(Long paymentId) {
        Payment payment = paymentRepository.findById(paymentId)
            .orElseThrow(() -> new PaymentException("Payment not found"));

        gateway.refund(payment.getTransactionId(), payment.getAmount());
        payment.markAsRefunded();
        paymentRepository.save(payment);
    }
}
