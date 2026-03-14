package com.example.shop.service;

import com.example.shop.model.Product;
import com.example.shop.model.Category;
import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Product search service.
 * Provides keyword search, category filtering, and price range filtering.
 */
public class ProductSearchService {
    private final ProductRepository productRepository;

    public ProductSearchService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    public List<Product> searchByKeyword(String keyword) {
        return productRepository.findAll().stream()
            .filter(p -> p.getName().contains(keyword)
                      || p.getDescription().contains(keyword))
            .filter(Product::isActive)
            .collect(Collectors.toList());
    }

    public List<Product> filterByCategory(Category category) {
        return productRepository.findByCategory(category).stream()
            .filter(Product::isActive)
            .collect(Collectors.toList());
    }

    public List<Product> filterByPriceRange(BigDecimal min, BigDecimal max) {
        return productRepository.findAll().stream()
            .filter(p -> p.getPrice().compareTo(min) >= 0
                      && p.getPrice().compareTo(max) <= 0)
            .filter(Product::isActive)
            .collect(Collectors.toList());
    }

    public List<Product> recommend(Product product) {
        return productRepository.findByCategory(product.getCategory()).stream()
            .filter(p -> !p.getId().equals(product.getId()))
            .filter(Product::isActive)
            .limit(5)
            .collect(Collectors.toList());
    }
}
