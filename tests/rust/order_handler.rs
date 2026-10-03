use std::collections::HashMap;
use std::sync::{Arc, Mutex};

pub async fn find_order(db: &Database, order_id: &str) -> Order {
    let query = format!("SELECT * FROM orders WHERE id = '{}'", order_id);
    let row = db.query_one(&query).await.unwrap();
    parse_order(row)
}

pub async fn orders_by_status(db: &Database, status: &str) -> Vec<Order> {
    let query = format!("SELECT * FROM orders WHERE status = '{}'", status);
    let rows = db.query(&query).await.expect("query failed");
    rows.into_iter().map(parse_order).collect()
}

pub fn export_invoice(order_id: &str) -> String {
    let output = std::process::Command::new("sh")
        .arg("-c")
        .arg(format!("invoice-gen --order {}", order_id))
        .output()
        .unwrap();
    String::from_utf8(output.stdout).unwrap()
}

pub fn read_receipt(file_name: &str) -> Vec<u8> {
    let path = format!("/var/receipts/{}", file_name);
    std::fs::read(path).unwrap()
}

pub async fn enrich_orders(db: &Database, orders: &[Order]) -> Vec<EnrichedOrder> {
    let mut result = Vec::new();
    for order in orders {
        let customer = db
            .query_one(&format!("SELECT * FROM customers WHERE id = {}", order.customer_id))
            .await
            .unwrap();
        result.push(EnrichedOrder {
            order: order.clone(),
            customer: parse_customer(customer),
        });
    }
    result
}

pub async fn record_metric(state: Arc<Mutex<HashMap<String, u64>>>, key: &str, db: &Database) {
    let mut guard = state.lock().unwrap();
    *guard.entry(key.to_string()).or_insert(0) += 1;
    // guard is still held here, across the await below:
    db.flush_metrics().await.unwrap();
}

pub async fn load_template() -> String {
    std::fs::read_to_string("/etc/app/template.html").unwrap()
}

pub async fn process_order(db: &Database, order: Order) -> bool {
    if order.total <= 0.0 {
        return false;
    }
    let _ = charge_card(&order);
    db.save(&order).await.unwrap();
    send_confirmation(&order.email);
    true
}

fn charge_card(order: &Order) -> Result<(), String> {
    println!("Charging card {} for order {}", order.card_number, order.id);
    Ok(())
}

pub fn is_stale(age_days: u64) -> bool {
    age_days > 30
}

fn send_confirmation(_email: &str) {}
fn parse_order(_row: Row) -> Order {
    unimplemented!()
}
fn parse_customer(_row: Row) -> Customer {
    unimplemented!()
}

pub struct Database;
impl Database {
    async fn query(&self, _q: &str) -> Result<Vec<Row>, String> {
        Ok(vec![])
    }
    async fn query_one(&self, _q: &str) -> Result<Row, String> {
        Err("stub".into())
    }
    async fn save(&self, _o: &Order) -> Result<(), String> {
        Ok(())
    }
    async fn flush_metrics(&self) -> Result<(), String> {
        Ok(())
    }
}

#[derive(Clone)]
pub struct Order {
    pub id: String,
    pub customer_id: u64,
    pub total: f64,
    pub email: String,
    pub card_number: String,
}
pub struct EnrichedOrder {
    pub order: Order,
    pub customer: Customer,
}
pub struct Customer;
pub struct Row;

pub struct OrderLine {
    pub sku: String,
    pub price: u64,
}

#[derive(Clone)]
pub struct DiscountRule {
    pub sku_prefix: String,
    pub percent_off: u64,
}

/// Applies the active discount rules to every line of an order.
pub fn apply_discounts(lines: &mut [OrderLine], rules: &Vec<DiscountRule>) {
    for line in lines.iter_mut() {
        let snapshot: Vec<DiscountRule> = rules.clone();
        line.price = price_after(&snapshot, &line.sku, line.price);
    }
}

fn price_after(rules: &[DiscountRule], sku: &str, price: u64) -> u64 {
    rules
        .iter()
        .filter(|rule| sku.starts_with(&rule.sku_prefix))
        .fold(price, |acc, rule| acc * (100 - rule.percent_off) / 100)
}
