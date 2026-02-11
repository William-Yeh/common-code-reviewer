// Test sample: Spring Boot order controller with intentional issues
// This file contains ~12 deliberate problems for the code review skill to catch.

package com.example.orders;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.jdbc.core.JdbcTemplate;
import javax.persistence.*;
import java.util.*;

// [ISSUE: Entity exposed directly as REST resource — no DTO separation]
@Entity
@Table(name = "orders")
class Order {
    @Id @GeneratedValue
    private Long id;
    private String customerId;
    private String product;
    private int quantity;
    private double price; // [ISSUE: double for money — floating point precision]

    // getters/setters omitted for brevity
    public Long getId() { return id; }
    public String getCustomerId() { return customerId; }
    public String getProduct() { return product; }
    public int getQuantity() { return quantity; }
    public double getPrice() { return price; }
    public void setId(Long id) { this.id = id; }
    public void setCustomerId(String customerId) { this.customerId = customerId; }
    public void setProduct(String product) { this.product = product; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
    public void setPrice(double price) { this.price = price; }
}

// [ISSUE: God class — controller + service + repository combined]
@RestController
@RequestMapping("/orders")
public class OrderController {

    // [ISSUE: Field injection — should use constructor injection]
    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private EntityManager entityManager;

    // [ISSUE: Global mutable cache — not thread-safe]
    private Map cache = new HashMap(); // [ISSUE: Raw type — no generics]

    @GetMapping
    public List getAllOrders() { // [ISSUE: Raw type List without generic parameter]
        // [ISSUE: Unbounded query — no pagination]
        return entityManager.createQuery("SELECT o FROM Order o").getResultList();
    }

    @PostMapping
    public Order createOrder(@RequestBody Order order) {
        // [ISSUE: No @Valid, entity used as request body — no input validation]

        // [ISSUE: SQL injection via string concatenation]
        jdbcTemplate.execute(
            "INSERT INTO orders (customer_id, product, quantity, price) VALUES ('"
            + order.getCustomerId() + "', '"
            + order.getProduct() + "', "
            + order.getQuantity() + ", "
            + order.getPrice() + ")"
        );

        // [ISSUE: No @Transactional — mixed read/write without transaction boundary]
        if (order.getQuantity() > 500) {
            try {
                notifyWarehouse(order);
            } catch (Exception e) {
                // [ISSUE: Catch Exception broadly, print stack trace]
                e.printStackTrace();
            }
        }

        cache.put(order.getId(), order);
        return order; // [ISSUE: Returning entity directly — exposes internal representation]
    }

    @GetMapping("/search")
    public List<Order> searchOrders(@RequestParam String customerId, @RequestParam String status) {
        // [ISSUE: SQL injection via string concatenation]
        String query = "SELECT * FROM orders WHERE customer_id = '" + customerId
            + "' AND status = '" + status + "'";
        return jdbcTemplate.queryForList(query).stream()
            .map(row -> {
                Order o = new Order();
                o.setId((Long) row.get("id"));
                o.setCustomerId((String) row.get("customer_id"));
                return o;
            })
            .collect(java.util.stream.Collectors.toList()); // [ISSUE: Could use .toList() on JDK 16+]
    }

    private void notifyWarehouse(Order order) throws Exception {
        // [ISSUE: throws Exception — too broad]
        java.net.HttpURLConnection conn = (java.net.HttpURLConnection)
            new java.net.URL("http://warehouse-service/notify").openConnection();
        conn.setRequestMethod("POST");
        conn.setDoOutput(true);
        // [ISSUE: No timeout set, no resource cleanup with try-with-resources]
        conn.getOutputStream().write(order.toString().getBytes());
        // [ISSUE: Response not checked]
        conn.getInputStream().read();
    }
}
