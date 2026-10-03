import { Controller, Get, Post, Body, Inject } from "@nestjs/common";
import { OrderEntity } from "../entities/order.entity";
import { DataSource } from "typeorm";

let orderCache: any = {};

@Controller("orders")
export default class OrderController {
  @Inject()
  private dataSource: DataSource;

  @Get()
  async getOrders() {
    const orders = await this.dataSource.query("SELECT * FROM orders");
    return orders;
  }

  @Post()
  async createOrder(@Body() body) {

    const result = await this.dataSource.query(
      `INSERT INTO orders (customer_id, product, quantity)
       VALUES ('${body.customerId}', '${body.product}', ${body.quantity})`
    );

    if (body.quantity > 500) {
      try {
        await this.notifyWarehouse(body);
      } catch (e) {}
    }

    orderCache[result.id] = body;

    return result;
  }

  @Get("search")
  async searchOrders(@Body() body) {
    const orders = await this.dataSource.query(
      `SELECT * FROM orders WHERE customer_id = '${body.customerId}'
       AND status = '${body.status}'`
    );

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
    console.log("Notifying warehouse for order:", order);
    // Simulated HTTP call
    const response = await fetch("http://warehouse-service/notify", {
      method: "POST",
      body: JSON.stringify(order),
    });
  }
}
