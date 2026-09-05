"""Checkout pricing for the storefront."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

COUPONS: dict[str, Decimal] = {
    "SAVE5": Decimal("5"),
    "SAVE20": Decimal("20"),
}


@dataclass(frozen=True)
class LineItem:
    sku: str
    unit_price: Decimal
    quantity: int
    category: str


@dataclass(frozen=True)
class Customer:
    tier: str
    country: str
    coupon: str | None = None


@dataclass
class Quote:
    subtotal: Decimal = Decimal("0")
    discount: Decimal = Decimal("0")
    shipping: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    notes: list[str] = field(default_factory=list)

    @property
    def total(self) -> Decimal:
        return self.subtotal - self.discount + self.shipping + self.tax


def quote_price(
    items: list[LineItem], customer: Customer, tax_rates: dict[str, Decimal]
) -> Quote:
    quote = Quote()
    for item in items:
        if item.quantity <= 0:
            raise ValueError(f"quantity must be positive for {item.sku}")
        line = item.unit_price * item.quantity
        if item.category == "digital" and customer.country != "US":
            quote.notes.append(f"digital VAT applies to {item.sku}")
        quote.subtotal += line
    if customer.tier == "gold" or customer.tier == "platinum":
        quote.discount += quote.subtotal * Decimal("0.10")
    if customer.coupon:
        try:
            quote.discount += coupon_value(customer.coupon, quote.subtotal)
        except KeyError:
            quote.notes.append(f"unknown coupon {customer.coupon} ignored")
    quote.shipping = (
        Decimal("0") if quote.subtotal > 100 else shipping_band(items, customer)
    )
    quote.tax = (quote.subtotal - quote.discount) * tax_rates.get(
        customer.country, Decimal("0")
    )
    return quote


def apply_promotions(quote: Quote, promotions: list[str], customer: Customer) -> Quote:
    for promo in promotions:
        if promo == "free-shipping":
            quote.shipping = Decimal("0")
        elif promo == "welcome" and customer.tier == "new":
            quote.discount += Decimal("5")
        elif promo.startswith("pct-"):
            percent = Decimal(promo.removeprefix("pct-")) / 100
            quote.discount += quote.subtotal * percent
        else:
            quote.notes.append(f"unsupported promotion {promo}")
    if quote.discount > quote.subtotal:
        quote.discount = quote.subtotal
    return quote


def shipping_band(items: list[LineItem], customer: Customer) -> Decimal:
    weight_units = sum(item.quantity for item in items)
    if customer.country != "US":
        return Decimal("25")
    if weight_units > 10:
        return Decimal("12")
    return Decimal("6")


def coupon_value(code: str, subtotal: Decimal) -> Decimal:
    value = COUPONS[code]
    return min(value, subtotal)
