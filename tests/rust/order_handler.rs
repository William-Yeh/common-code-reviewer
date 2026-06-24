// Test sample #1: Order handler — targets general SKILL.md principles + Rust rules
// Focuses on: Security, Error handling (unwrap/panic), Performance, Async, FP, SRP

use std::collections::HashMap;
use std::sync::{Arc, Mutex};

// [ISSUE: BLOCKER — SQL injection via format! string interpolation]
pub async fn find_order(db: &Database, order_id: &str) -> Order {
    let query = format!("SELECT * FROM orders WHERE id = '{}'", order_id);
    // [ISSUE: BLOCKER — .unwrap() in library code panics the caller on any DB error]
    let row = db.query_one(&query).await.unwrap();
    parse_order(row)
}

// [ISSUE: BLOCKER — SQL injection again; user-controlled status concatenated]
pub async fn orders_by_status(db: &Database, status: &str) -> Vec<Order> {
    let query = format!("SELECT * FROM orders WHERE status = '{}'", status);
    // [ISSUE: MAJOR — unbounded query, no LIMIT/pagination on a potentially huge table]
    let rows = db.query(&query).await.expect("query failed");
    rows.into_iter().map(parse_order).collect()
}

// [ISSUE: BLOCKER — command injection: unsanitized order_id passed to shell]
pub fn export_invoice(order_id: &str) -> String {
    let output = std::process::Command::new("sh")
        .arg("-c")
        .arg(format!("invoice-gen --order {}", order_id))
        .output()
        .unwrap();
    String::from_utf8(output.stdout).unwrap()
}

// [ISSUE: BLOCKER — path traversal: user-controlled file name in path]
pub fn read_receipt(file_name: &str) -> Vec<u8> {
    let path = format!("/var/receipts/{}", file_name);
    std::fs::read(path).unwrap()
}

// [ISSUE: MAJOR — N+1 query pattern: one DB round-trip per item inside a loop]
pub async fn enrich_orders(db: &Database, orders: &[Order]) -> Vec<EnrichedOrder> {
    let mut result = Vec::new();
    for order in orders {
        let customer = db
            .query_one(&format!("SELECT * FROM customers WHERE id = {}", order.customer_id))
            .await
            .unwrap();
        result.push(EnrichedOrder {
            order: order.clone(), // [ISSUE: MINOR — clone per iteration of an owned Order]
            customer: parse_customer(customer),
        });
    }
    result
}

// [ISSUE: MAJOR — Mutex held across .await; blocks the async executor / deadlock risk]
pub async fn record_metric(state: Arc<Mutex<HashMap<String, u64>>>, key: &str, db: &Database) {
    let mut guard = state.lock().unwrap();
    *guard.entry(key.to_string()).or_insert(0) += 1;
    // guard is still held here, across the await below:
    db.flush_metrics().await.unwrap();
}

// [ISSUE: BLOCKER — blocking std::fs call inside async fn stalls the runtime worker]
pub async fn load_template() -> String {
    std::fs::read_to_string("/etc/app/template.html").unwrap()
}

// [ISSUE: MAJOR — SRP: validates, charges payment, persists, AND emails in one function]
pub async fn process_order(db: &Database, order: Order) -> bool {
    if order.total <= 0.0 {
        return false; // [ISSUE: MINOR — bool return loses the reason for failure; use Result]
    }
    let _ = charge_card(&order); // [ISSUE: MAJOR — Result silently discarded; payment failure ignored]
    db.save(&order).await.unwrap();
    send_confirmation(&order.email);
    true
}

// [ISSUE: MINOR — sensitive data: full card number logged]
fn charge_card(order: &Order) -> Result<(), String> {
    println!("Charging card {} for order {}", order.card_number, order.id);
    Ok(())
}

// [ISSUE: NIT — magic number 30 unexplained]
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
