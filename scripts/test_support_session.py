"""Exercise the actual customer session controller with isolated platform stubs.

Only platform selection and generated branding are substituted. The gate,
stop/options controller, watch cancellation and password calls are the real code.
"""
from pathlib import Path
import subprocess

root = Path.cwd()
work = root / 'work/support-session-test'
(work / 'src').mkdir(parents=True, exist_ok=True)
source = (root / 'client/src/support.rs').read_text()
assert source.count('cfg!(all(any(windows, target_os = "macos"), feature = "custom-support"))') == 1
source = source.replace('cfg!(all(any(windows, target_os = "macos"), feature = "custom-support"))', 'true')
(work / 'src/support.rs').write_text(source)
(work / 'src/support_brand.rs').write_text("""
pub const CUSTOMER: bool = true;
pub const CONFIGURED: bool = true;
pub const APP_NAME: &str = "test";
pub const COMPANY_NAME: &str = "test";
pub const ID_SERVER: &str = "test.invalid";
pub const RELAY_SERVER: &str = "test.invalid";
pub const PUBLIC_KEY: &str = "test";
""")
(work / 'Cargo.toml').write_text("""
[package]
name = "support-session-controller-test"
version = "0.1.0"
edition = "2021"
[dependencies]
lazy_static = "=1.4.0"
tokio = { version = "=1.28.2", features = ["sync", "macros", "rt", "time"] }
""")
(work / 'src/lib.rs').write_text(r'''
extern crate self as hbb_common;
pub use tokio;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
pub mod config {
    use std::{collections::HashMap, sync::{Mutex, RwLock}};
    lazy_static::lazy_static! {
        pub static ref APP_NAME: RwLock<String> = Default::default();
        pub static ref ORG: RwLock<String> = Default::default();
        pub static ref EXE_RENDEZVOUS_SERVER: RwLock<String> = Default::default();
        pub static ref OVERWRITE_SETTINGS: RwLock<HashMap<String,String>> = Default::default();
        pub static ref BUILTIN_SETTINGS: RwLock<HashMap<String,String>> = Default::default();
        pub static ref HARD_SETTINGS: RwLock<HashMap<String,String>> = Default::default();
        static ref OPTIONS: Mutex<HashMap<String,String>> = Default::default();
    }
    pub struct Config;
    impl Config {
        pub fn get_bool_option(key: &str) -> bool { Self::get_option(key) == "Y" }
        pub fn get_option(key: &str) -> String { OPTIONS.lock().unwrap().get(key).cloned().unwrap_or_default() }
        pub fn set_option(key: String, value: String) { OPTIONS.lock().unwrap().insert(key,value); }
        pub fn set_options(value: HashMap<String,String>) { *OPTIONS.lock().unwrap() = value; }
    }
}
pub mod password_security {
    use super::*;
    pub static ROTATIONS: AtomicUsize = AtomicUsize::new(0);
    pub fn update_temporary_password() { ROTATIONS.fetch_add(1, Ordering::SeqCst); }
}
pub mod common {
    use super::*;
    pub static RUNNING: AtomicBool = AtomicBool::new(false);
    pub fn is_server_running() -> bool { RUNNING.load(Ordering::SeqCst) }
}
pub mod rendezvous_mediator {
    pub struct RendezvousMediator;
    impl RendezvousMediator { pub fn restart() {} }
}
mod support;

#[tokio::test(flavor = "current_thread")]
async fn startup_stale_options_and_stop_preserve_explicit_consent() {
    use std::{collections::HashMap, time::Duration};
    support::configure();
    assert!(!support::enabled());
    let before = password_security::ROTATIONS.load(Ordering::SeqCst);
    assert!(!support::set_enabled(true).is_empty(), "early Start must be refused");
    assert_eq!(before, password_security::ROTATIONS.load(Ordering::SeqCst));
    common::RUNNING.store(true, Ordering::SeqCst);
    assert!(support::set_enabled(true).is_empty());
    assert!(support::enabled());
    let mut receiver = support::subscribe();
    let rotations = password_security::ROTATIONS.load(Ordering::SeqCst);
    for _ in 0..1000 {
        support::set_options(HashMap::from([("stop-service".into(),"Y".into()),("enable-keyboard".into(),"Y".into())]));
        assert!(support::enabled(), "stale CM options cannot stop an open session");
    }
    assert_eq!(rotations, password_security::ROTATIONS.load(Ordering::SeqCst), "polls must not rotate the password");
    assert!(tokio::time::timeout(Duration::from_millis(20), support::wait_until_stopped(&mut receiver)).await.is_err());
    assert!(support::set_enabled(false).is_empty());
    assert!(support::set_enabled(true).is_empty());
    tokio::time::timeout(Duration::from_millis(100), support::wait_until_stopped(&mut receiver)).await.expect("Stop must invalidate old connections even after rapid restart");
    support::set_enabled(false);
    support::set_options(HashMap::new());
    assert!(!support::enabled(), "stale running options must never reopen a closed session");
    assert!(config::Config::get_bool_option("stop-service"));
}
''')
subprocess.run(['cargo', 'test', '--manifest-path', str(work / 'Cargo.toml')], check=True)
