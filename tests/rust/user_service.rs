// Test sample #2: User service — targets general SKILL.md principles + Rust idioms
// Focuses on: OCP, ISP, DIP, Architecture, FP, Testability, Clean Code,
//             plus Rust-specific: unsafe/SAFETY, Box<dyn Error> in lib API,
//             Arc<Mutex> overuse, clone-to-compile, newtype/enum design.

use std::collections::HashMap;
use std::error::Error;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

// ─── ISP: Fat trait ─────────────────────────────────────────────────
// [ISSUE: ISP — 8 methods; a read-only consumer must implement all of them]
pub trait UserStore {
    fn find_by_id(&self, id: &str) -> Option<User>;
    fn find_by_email(&self, email: &str) -> Option<User>;
    fn save(&mut self, user: User) -> Result<(), Box<dyn Error>>;
    fn delete(&mut self, id: &str) -> Result<(), Box<dyn Error>>;
    fn bulk_import(&mut self, users: Vec<User>) -> Result<usize, Box<dyn Error>>;
    fn export_csv(&self) -> Result<String, Box<dyn Error>>;
    fn generate_report(&self) -> Result<Vec<u8>, Box<dyn Error>>;
    fn archive_inactive(&mut self, days: u64) -> Result<usize, Box<dyn Error>>;
}

// ─── OCP: match on action string ────────────────────────────────────
// [ISSUE: OCP — stringly-typed; every new action edits this function]
// [ISSUE: Rust — `action: &str` should be an enum so the match is exhaustive]
pub fn handle_user_action(action: &str, user_id: &str) -> Result<(), Box<dyn Error>> {
    match action {
        "activate" => {
            println!("Activating {}", user_id);
            Ok(())
        }
        "deactivate" => {
            println!("Deactivating {}", user_id);
            Ok(())
        }
        "suspend" => {
            println!("Suspending {}", user_id);
            Ok(())
        }
        "promote" => {
            println!("Promoting {}", user_id);
            Ok(())
        }
        // [ISSUE: unknown actions silently succeed]
        _ => Ok(()),
    }
}

// ─── Architecture: anemic domain + stringly-typed fields ────────────
// [ISSUE: Anemic domain — pure data bag, all behavior lives elsewhere]
#[derive(Clone)]
pub struct User {
    pub id: String,
    pub name: String,
    pub email: String,
    pub role: String,   // [ISSUE: Rust — should be a Role enum, not String]
    pub status: String, // [ISSUE: Rust — should be a Status enum, not String]
    pub last_login: u64,
}

// ─── FP: hidden side effects + non-determinism ──────────────────────
// [ISSUE: FP — named "count" but writes a file (hidden side effect)]
// [ISSUE: Testability — SystemTime::now() makes this non-deterministic]
pub fn count_active_users(users: &[User]) -> usize {
    let count = users.iter().filter(|u| u.status == "active").count();
    let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
    let line = format!("{}: {}\n", now, count);
    std::fs::write("/tmp/user-stats.txt", line).unwrap(); // [ISSUE: side effect + unwrap]
    count
}

// ─── Testability: hard-coded dependencies ───────────────────────────
pub struct UserService {
    // [ISSUE: no injected dependencies — uses hardcoded paths/globals]
    cache: Arc<Mutex<HashMap<String, User>>>, // [ISSUE: Rust — Arc<Mutex> where single ownership would do]
}

impl UserService {
    // [ISSUE: Testability — hardcoded filesystem path, untestable]
    pub fn load_config(&self) -> Result<HashMap<String, String>, Box<dyn Error>> {
        let data = std::fs::read_to_string("/etc/app/users.json")?;
        let config = parse_kv(&data);
        Ok(config)
    }

    // [ISSUE: Rust — clone-to-compile: clones the whole User just to insert]
    pub fn cache_user(&self, user: &User) {
        let mut guard = self.cache.lock().unwrap();
        guard.insert(user.id.clone(), user.clone());
    }

    // ─── Clean Code: deep nesting (4 levels) ────────────────────────
    pub fn deactivate_inactive(&self, users: &[User], days: u64) -> Vec<User> {
        let mut result = Vec::new();
        for u in users {
            if u.last_login != 0 {
                if now_secs() - u.last_login > days * 86400 {
                    if u.role != "admin" {
                        if u.status != "protected" {
                            let mut updated = u.clone();
                            updated.status = "inactive".to_string();
                            result.push(updated);
                        }
                    }
                }
            }
        }
        result
    }
}

// ─── Rust: unsafe without SAFETY justification ──────────────────────
// [ISSUE: unsafe block with no // SAFETY: comment; and a safe alternative exists]
pub fn first_byte(data: &[u8]) -> u8 {
    unsafe { *data.get_unchecked(0) }
}

// [ISSUE: Clean Code — bad naming: what are `d`, `f`, `r`, `x`?]
fn proc(d: &[User], f: &str) -> Vec<User> {
    let mut r = Vec::new();
    for x in d {
        if x.role == f {
            r.push(x.clone()); // [ISSUE: clone in loop]
        }
    }
    r
}

// [ISSUE: Dead code — never called]
fn old_notify(email: &str, msg: &str) {
    println!("Sending to {}: {}", email, msg);
}

// ─── DIP: depends on concrete type, not abstraction ─────────────────
// [ISSUE: DIP — takes a concrete PostgresStore instead of `&mut impl UserStore`]
pub fn remove_user(store: &mut PostgresStore, id: &str) -> Result<(), Box<dyn Error>> {
    store.delete(id)
}

fn parse_kv(_s: &str) -> HashMap<String, String> {
    HashMap::new()
}
fn now_secs() -> u64 {
    SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs()
}

pub struct PostgresStore;
impl UserStore for PostgresStore {
    fn find_by_id(&self, _id: &str) -> Option<User> {
        None
    }
    fn find_by_email(&self, _email: &str) -> Option<User> {
        None
    }
    fn save(&mut self, _user: User) -> Result<(), Box<dyn Error>> {
        Ok(())
    }
    fn delete(&mut self, _id: &str) -> Result<(), Box<dyn Error>> {
        Ok(())
    }
    fn bulk_import(&mut self, _users: Vec<User>) -> Result<usize, Box<dyn Error>> {
        Ok(0)
    }
    fn export_csv(&self) -> Result<String, Box<dyn Error>> {
        Ok(String::new())
    }
    fn generate_report(&self) -> Result<Vec<u8>, Box<dyn Error>> {
        Ok(Vec::new())
    }
    fn archive_inactive(&mut self, _days: u64) -> Result<usize, Box<dyn Error>> {
        Ok(0)
    }
}
