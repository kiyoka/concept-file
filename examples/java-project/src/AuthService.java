package com.example.shop.service;

import com.example.shop.model.User;
import java.time.LocalDateTime;

/**
 * Service responsible for user authentication.
 * Handles login, logout, token issuance and validation.
 */
public class AuthService {
    private final UserRepository userRepository;
    private final TokenProvider tokenProvider;

    public AuthService(UserRepository userRepository, TokenProvider tokenProvider) {
        this.userRepository = userRepository;
        this.tokenProvider = tokenProvider;
    }

    public AuthResult login(String email, String password) {
        User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new AuthException("User not found"));

        if (!user.verifyPassword(password)) {
            throw new AuthException("Invalid password");
        }

        user.setLastLoginAt(LocalDateTime.now());
        userRepository.save(user);

        String token = tokenProvider.generateToken(user.getId());
        return new AuthResult(token, user);
    }

    public void logout(String token) {
        tokenProvider.invalidate(token);
    }

    public User authenticate(String token) {
        Long userId = tokenProvider.validateAndGetUserId(token);
        return userRepository.findById(userId)
            .orElseThrow(() -> new AuthException("User not found"));
    }
}
