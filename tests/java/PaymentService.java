// Test sample #2: Payment processing — targets general SKILL.md principles
// Focuses on: OCP, LSP, ISP, Testability, Clean Code, Architecture, FP, Security

package com.example.payments;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.LocalDateTime;
import java.util.*;

// ─── ISP: Fat interface ─────────────────────────────────────────────
// [ISSUE: ISP violation — implementors must provide all 7 methods even if they only process payments]
interface PaymentProcessor {
    void processPayment(Map<String, Object> payment);
    void refund(String transactionId, double amount);
    void subscribe(String customerId, String planId);
    void cancelSubscription(String subscriptionId);
    String generateInvoice(String transactionId);
    Map<String, Object> getAnalytics(String startDate, String endDate);
    void exportTransactions(String format, OutputStream out);
}

// ─── LSP: Subtype contract violation ────────────────────────────────
abstract class PaymentGateway {
    /**
     * Process a payment. Returns a transaction ID on success.
     * Contract: never returns null; throws PaymentException on failure.
     */
    abstract String pay(double amount, String currency);
}

class StripeGateway extends PaymentGateway {
    @Override
    String pay(double amount, String currency) {
        // Correct implementation — returns transaction ID
        return "txn_stripe_" + System.currentTimeMillis();
    }
}

// [ISSUE: LSP violation — returns null instead of throwing, breaking the contract]
class LegacyGateway extends PaymentGateway {
    @Override
    String pay(double amount, String currency) {
        if (amount > 10000) {
            return null; // Violates contract: callers don't expect null
        }
        return "txn_legacy_" + System.currentTimeMillis();
    }
}

// ─── OCP: Switch on payment type ────────────────────────────────────
class PaymentService {

    // [ISSUE: Tight coupling — domain logic imports infrastructure directly]
    private final HttpURLConnection connection;

    PaymentService() throws Exception {
        // [ISSUE: Hard-coded URL — not configurable, not injectable]
        this.connection = (HttpURLConnection) new URL("http://payment-gateway.internal").openConnection();
    }

    // [ISSUE: OCP violation — every new payment method requires modifying this switch]
    public Map<String, Object> processPayment(String method, Map<String, Object> details) {
        double amount = (double) details.get("amount"); // [ISSUE: Unsafe cast from Object — ClassCastException risk]

        Map<String, Object> result = new HashMap<>();

        switch (method) {
            case "credit_card":
                // [ISSUE: Deep nesting — 3 levels inside switch case]
                if (details.containsKey("card_number")) {
                    String card = (String) details.get("card_number");
                    if (card.length() == 16) {
                        if (amount > 0 && amount < 100000) {
                            result.put("status", "processed");
                            result.put("method", "credit_card");
                            // [ISSUE: Sensitive data logged — card number in plain text]
                            System.out.println("Processing card: " + card + " for $" + amount);
                        }
                    }
                }
                break;
            case "bank_transfer":
                result.put("status", "pending");
                result.put("method", "bank_transfer");
                break;
            case "paypal":
                result.put("status", "redirecting");
                result.put("method", "paypal");
                break;
            case "crypto":
                result.put("status", "awaiting_confirmation");
                result.put("method", "crypto");
                break;
            // [ISSUE: No default case — unknown methods silently return empty map]
        }

        return result;
    }

    // ─── FP: Hidden side effects ────────────────────────────────────
    // [ISSUE: Named "calculate" but has side effects — writes file and logs]
    public double calculateFee(double amount, String method) {
        double fee;
        if ("credit_card".equals(method)) {
            fee = amount * 0.029 + 0.30; // [ISSUE: Magic numbers — what is 0.029 and 0.30?]
        } else if ("bank_transfer".equals(method)) {
            fee = 1.50;
        } else {
            fee = amount * 0.05;
        }

        // [ISSUE: Side effect hidden in a "calculate" method]
        try {
            FileWriter fw = new FileWriter("/var/log/fees.log", true); // [ISSUE: No try-with-resources]
            fw.write(LocalDateTime.now() + ": " + method + " fee=$" + fee + "\n");
            fw.close();
        } catch (IOException e) {
            // [ISSUE: Exception silently swallowed]
        }

        return fee;
    }

    // ─── Testability ────────────────────────────────────────────────
    // [ISSUE: Non-deterministic — uses LocalDateTime.now() directly]
    public boolean isWithinRefundWindow(LocalDateTime purchaseDate) {
        return LocalDateTime.now().minusDays(30).isBefore(purchaseDate);
    }

    // [ISSUE: Hard-coded file dependency — untestable without real filesystem]
    public Properties loadGatewayConfig() {
        Properties props = new Properties();
        try {
            props.load(new FileInputStream("/etc/payments/gateway.properties"));
        } catch (IOException e) {
            e.printStackTrace(); // [ISSUE: printStackTrace in production]
        }
        return props;
    }

    // ─── Clean Code ─────────────────────────────────────────────────
    // [ISSUE: Mixed abstraction levels — config reading, validation, API call, logging]
    public Map<String, Object> refund(String txnId, double amt) {
        Properties config = loadGatewayConfig();
        String endpoint = config.getProperty("refund_url", "http://gateway/refund");

        // [ISSUE: Code duplication — same amount validation as processPayment]
        if (amt <= 0 || amt >= 100000) {
            return Map.of("error", "invalid amount");
        }

        // [ISSUE: Dead code — variable computed but never used]
        String debugTimestamp = LocalDateTime.now().toString();

        Map<String, Object> response = new HashMap<>();
        response.put("txn_id", txnId);
        response.put("amount", amt);
        response.put("status", "refunded");
        return response;
    }
}

// ─── Clean Code: Bad naming ─────────────────────────────────────────
// [ISSUE: Non-descriptive class and method names]
class Util {
    // [ISSUE: Name "process" tells you nothing about what it does]
    static List<Map<String, Object>> process(List<Map<String, Object>> data, int t) {
        List<Map<String, Object>> res = new ArrayList<>();
        for (Map<String, Object> d : data) {
            // [ISSUE: Duplicated amount validation — third time this check appears]
            double a = (double) d.getOrDefault("amount", 0.0);
            if (a > 0 && a < t) {
                res.add(d);
            }
        }
        return res;
    }
}

// ─── Architecture: Anemic domain model ──────────────────────────────
// [ISSUE: Entity is a pure data bag — all logic in PaymentService above]
class Payment {
    String id;
    String method;              // [ISSUE: String-typed — should be enum or sealed type]
    double amount;              // [ISSUE: double for money]
    String currency;
    String status;              // [ISSUE: String-typed — should be enum or sealed type]
    LocalDateTime createdAt;
    LocalDateTime updatedAt;

    // [ISSUE: No-arg constructor + public mutable fields — no encapsulation]
}

// ─── Security ───────────────────────────────────────────────────────
class PaymentExporter {
    // [ISSUE: No authorization check — any caller can export all transactions]
    // [ISSUE: Command injection — unsanitized format param passed to ProcessBuilder shell command]
    public void exportAll(String format, OutputStream out) throws Exception {
        ProcessBuilder pb = new ProcessBuilder("sh", "-c", "payment-export --format " + format);
        pb.start();
    }
}
