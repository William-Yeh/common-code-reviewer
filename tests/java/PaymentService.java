package com.example.payments;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.LocalDateTime;
import java.util.*;

// ─── ISP: Fat interface ─────────────────────────────────────────────
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

    private final HttpURLConnection connection;

    PaymentService() throws Exception {
        this.connection = (HttpURLConnection) new URL("http://payment-gateway.internal").openConnection();
    }

    public Map<String, Object> processPayment(String method, Map<String, Object> details) {
        double amount = (double) details.get("amount");

        Map<String, Object> result = new HashMap<>();

        switch (method) {
            case "credit_card":
                if (details.containsKey("card_number")) {
                    String card = (String) details.get("card_number");
                    if (card.length() == 16) {
                        if (amount > 0 && amount < 100000) {
                            result.put("status", "processed");
                            result.put("method", "credit_card");
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
        }

        return result;
    }

    // ─── FP: Hidden side effects ────────────────────────────────────
    public double calculateFee(double amount, String method) {
        double fee;
        if ("credit_card".equals(method)) {
            fee = amount * 0.029 + 0.30;
        } else if ("bank_transfer".equals(method)) {
            fee = 1.50;
        } else {
            fee = amount * 0.05;
        }

        try {
            FileWriter fw = new FileWriter("/var/log/fees.log", true);
            fw.write(LocalDateTime.now() + ": " + method + " fee=$" + fee + "\n");
            fw.close();
        } catch (IOException e) {
        }

        return fee;
    }

    // ─── Testability ────────────────────────────────────────────────
    public boolean isWithinRefundWindow(LocalDateTime purchaseDate) {
        return LocalDateTime.now().minusDays(30).isBefore(purchaseDate);
    }

    public Properties loadGatewayConfig() {
        Properties props = new Properties();
        try {
            props.load(new FileInputStream("/etc/payments/gateway.properties"));
        } catch (IOException e) {
            e.printStackTrace();
        }
        return props;
    }

    // ─── Clean Code ─────────────────────────────────────────────────
    public Map<String, Object> refund(String txnId, double amt) {
        Properties config = loadGatewayConfig();
        String endpoint = config.getProperty("refund_url", "http://gateway/refund");

        if (amt <= 0 || amt >= 100000) {
            return Map.of("error", "invalid amount");
        }

        String debugTimestamp = LocalDateTime.now().toString();

        Map<String, Object> response = new HashMap<>();
        response.put("txn_id", txnId);
        response.put("amount", amt);
        response.put("status", "refunded");
        return response;
    }
}

// ─── Clean Code: Bad naming ─────────────────────────────────────────
class Util {
    static List<Map<String, Object>> process(List<Map<String, Object>> data, int t) {
        List<Map<String, Object>> res = new ArrayList<>();
        for (Map<String, Object> d : data) {
            double a = (double) d.getOrDefault("amount", 0.0);
            if (a > 0 && a < t) {
                res.add(d);
            }
        }
        return res;
    }
}

// ─── Architecture: Anemic domain model ──────────────────────────────
class Payment {
    String id;
    String method;
    double amount;
    String currency;
    String status;
    LocalDateTime createdAt;
    LocalDateTime updatedAt;

}

// ─── Security ───────────────────────────────────────────────────────
class PaymentExporter {
    public void exportAll(String format, OutputStream out) throws Exception {
        ProcessBuilder pb = new ProcessBuilder("sh", "-c", "payment-export --format " + format);
        pb.start();
    }
}
