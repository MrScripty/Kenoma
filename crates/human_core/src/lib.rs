#![doc = include_str!("../README.md")]
//! Deterministic graph-to-mesh tools, independent of simulation and rendering.
mod edit;
mod generate;
mod samples;
mod types;
mod validation;
pub use edit::*;
pub use generate::*;
pub use glam::{Quat, Vec2, Vec3};
pub use samples::*;
pub use types::*;
pub use validation::*;
