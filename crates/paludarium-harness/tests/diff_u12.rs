//! U12 fixed guest operation. The Python supervisor owns the hard deadline.
#[path = "support/u10.rs"]
mod support;

#[test]
fn u10_guest_operation() {
    if std::env::var_os("PALUDARIUM_U10_OPERATION").is_some() {
        support::operation();
    }
}
