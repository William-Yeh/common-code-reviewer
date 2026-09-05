from decimal import Decimal
import pytest
from pricing_engine import Customer, LineItem, Quote, apply_promotions, quote_price

def test_quote_rejects_non_positive_quantity():
    with pytest.raises(ValueError):
        quote_price([LineItem("A", Decimal("10"), 0, "physical")], Customer("new", "US"), {})

def test_promotions_cover_every_branch():
    q = Quote(subtotal=Decimal("50"), shipping=Decimal("6"))
    apply_promotions(q, ["free-shipping", "welcome", "pct-10", "bogus"], Customer("new", "US"))
    assert q.shipping == 0
    assert q.discount == Decimal("10")
    assert q.notes == ["unsupported promotion bogus"]
    q2 = apply_promotions(Quote(subtotal=Decimal("1")), ["pct-500"], Customer("gold", "US"))
    assert q2.discount == Decimal("1")

def test_total_property():
    assert Quote(subtotal=Decimal("10"), tax=Decimal("1")).total == Decimal("11")
