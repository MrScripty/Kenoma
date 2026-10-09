# Canonical graph sample project

`skin_graph_samples.human.sqlite` stores only source parameters and options.
Record IDs: 1 isolated node; 2 straight edge; 3 three-edge bent chain;
4 three-edge branch; 5 missing explicit root; 6 schematic human.

Regenerate to a **new** path with:

```sh
cargo run -p human_persistence --example samples -- /tmp/skin_graph_samples.human.sqlite
```

The persistence test compares this fixture's source with `sample_graphs()` and
checks regenerated vertex/triangle counts. The core tests independently check
edge topology, outward winding, unit normals and deterministic triangle order.
No generated meshes or research data are stored here.
