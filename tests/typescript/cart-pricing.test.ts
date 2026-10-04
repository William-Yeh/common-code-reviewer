import { describe, expect, it, vi } from "vitest";
import { CartPricing } from "./cart-pricing";

describe("CartPricing", () => {
  it("applies the bulk discount", () => {
    const pricing = new CartPricing();
    const rounding = vi.spyOn(pricing as any, "roundToCents");
    pricing.total([{ sku: "A", price: 10, quantity: 12 }]);
    expect(rounding).toHaveBeenCalledTimes(1);
    expect((pricing as any).lastDiscountRate).toBe(0.1);
  });

  it("charges full price under the bulk threshold", () => {
    const pricing = new CartPricing();
    expect(pricing.total([{ sku: "A", price: 10, quantity: 2 }])).toBe(20);
  });
});
