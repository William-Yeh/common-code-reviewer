use std::rc::Rc;

pub async fn process_shared_name() -> usize {
    let name = Rc::new(String::from("customer"));
    tokio::task::yield_now().await;
    name.len()
}

pub fn spawn_processing() {
    tokio::spawn(process_shared_name());
}
