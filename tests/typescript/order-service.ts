// Test sample: NestJS order management service with intentional issues
// This file contains ~12 deliberate problems for the code review skill to catch.

import { Controller, Get, Post, Body, Inject } from "@nestjs/common";
import { OrderEntity } from "../entities/order.entity";
import { DataSource } from "typeorm";

// [ISSUE: Shared mutable state at module level]
let orderCache: any = {};

// [ISSUE: God service — controller + business logic + data access all in one]
@Controller("orders")
export default class OrderController {
  // [ISSUE: Field injection via @Inject, not constructor injection]
  @Inject()
  private dataSource: DataSource;

  @Get()
  async getOrders() {
    // [ISSUE: Unbounded query — no pagination, no LIMIT]
    const orders = await this.dataSource.query("SELECT * FROM orders");
    return orders;
  }

  @Post()
  async createOrder(@Body() body) {
    // [ISSUE: No DTO, no validation — raw body with implicit 'any']

    // [ISSUE: SQL injection — string interpolation in query]
    const result = await this.dataSource.query(
      `INSERT INTO orders (customer_id, product, quantity)
       VALUES ('${body.customerId}', '${body.product}', ${body.quantity})`
    );

    // [ISSUE: Magic number without explanation]
    if (body.quantity > 500) {
      // [ISSUE: Empty catch block — silently swallows error]
      try {
        await this.notifyWarehouse(body);
      } catch (e) {}
    }

    // [ISSUE: Caching with mutable module-level state + any type]
    orderCache[result.id] = body;

    // [ISSUE: Exposing entity directly as API response]
    return result;
  }

  @Get("search")
  async searchOrders(@Body() body) {
    // [ISSUE: SQL injection via string interpolation]
    const orders = await this.dataSource.query(
      `SELECT * FROM orders WHERE customer_id = '${body.customerId}'
       AND status = '${body.status}'`
    );

    // [ISSUE: forEach with side effect instead of map]
    const results: any[] = [];
    orders.forEach((order) => {
      results.push({
        id: order.id,
        total: order.price * order.quantity,
        status: order.status,
      });
    });

    return results;
  }

  private async notifyWarehouse(order: any): Promise<void> {
    // [ISSUE: console.log in production code]
    console.log("Notifying warehouse for order:", order);
    // Simulated HTTP call
    const response = await fetch("http://warehouse-service/notify", {
      method: "POST",
      body: JSON.stringify(order),
    });
    // [ISSUE: Response not checked for errors]
  }
}
