package com.example.orders;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.jdbc.core.JdbcTemplate;
import javax.persistence.*;
import java.util.*;

@Entity
@Table(name = "orders")
class Order {
    @Id @GeneratedValue
    private Long id;
    private String customerId;
    private String product;
    private int quantity;
    private double price;

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

@RestController
@RequestMapping("/orders")
public class OrderController {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private EntityManager entityManager;

    private Map cache = new HashMap();

    @GetMapping
    public List getAllOrders() {
        return entityManager.createQuery("SELECT o FROM Order o").getResultList();
    }

    @PostMapping
    public Order createOrder(@RequestBody Order order) {

        jdbcTemplate.execute(
            "INSERT INTO orders (customer_id, product, quantity, price) VALUES ('"
            + order.getCustomerId() + "', '"
            + order.getProduct() + "', "
            + order.getQuantity() + ", "
            + order.getPrice() + ")"
        );

        if (order.getQuantity() > 500) {
            try {
                notifyWarehouse(order);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        cache.put(order.getId(), order);
        return order;
    }

    @GetMapping("/search")
    public List<Order> searchOrders(@RequestParam String customerId, @RequestParam String status) {
        String query = "SELECT * FROM orders WHERE customer_id = '" + customerId
            + "' AND status = '" + status + "'";
        return jdbcTemplate.queryForList(query).stream()
            .map(row -> {
                Order o = new Order();
                o.setId((Long) row.get("id"));
                o.setCustomerId((String) row.get("customer_id"));
                return o;
            })
            .collect(java.util.stream.Collectors.toList());
    }

    private void notifyWarehouse(Order order) throws Exception {
        java.net.HttpURLConnection conn = (java.net.HttpURLConnection)
            new java.net.URL("http://warehouse-service/notify").openConnection();
        conn.setRequestMethod("POST");
        conn.setDoOutput(true);
        conn.getOutputStream().write(order.toString().getBytes());
        conn.getInputStream().read();
    }
}
