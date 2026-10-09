# Graph core

`lib.rs` is the public facade. `types.rs` defines the serializable contract;
`validation.rs` validates and derives stable island traversal; `generate.rs`
builds disposable geometry; `edit.rs` applies atomic commands and history;
`samples.rs` provides small deterministic assets. No I/O, UI or physics lives here.
