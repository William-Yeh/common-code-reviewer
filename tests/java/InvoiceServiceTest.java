package com.example.billing;

import static org.assertj.core.api.Assertions.assertThat;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class InvoiceServiceTest {

    private final InvoiceService service =
            new InvoiceService(new InMemoryInvoiceRepository(), new BigDecimal("0.21"));

    @Test
    void issuesInvoiceForPaidOrder() {
        service.issue("order-42", new BigDecimal("120.00"));
    }

    @Test
    void appliesVatToNetAmount() {
        Invoice invoice = service.issue("order-43", new BigDecimal("100.00"));

        assertThat(invoice.total()).isEqualByComparingTo("121.00");
    }
}
