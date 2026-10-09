# Simple graph project storage

This crate owns graph-only SQLite tables: `skin_graph_schema`, `skin_graphs`,
`skin_graph_nodes`, and `skin_graph_edges`. Schema/record version is 1. It does
not use the database-wide `user_version`, modify unrelated tables, or access
any research assets. Source nodes, edges, radii, root flags and generation options
are persisted; generated buffers and editor history are not.

`HumanProjectStore::open(path)` opens/creates a project; `in_memory()` is useful
for tests. `save_skin_graph_to_project(store, id, name, graph, options)` allocates
an ID for `None`, or atomically updates an existing supported record for `Some`.
`load_skin_graph_from_project(store, id)` returns `StoredSkinGraph` with name,
source graph and generation options from one database read snapshot. Both paths
validate source and resulting geometry. Future schema/record versions fail
without overwriting them. Read failures and write failures are typed `StoreError`.
Only root flag bit 0 is supported; unknown flags fail rather than being discarded.

Create a new sample project (refuses an existing output path):

```sh
cargo run -p human_persistence --example samples -- /tmp/demo.human.sqlite
```

The committed fixture is at `assets/samples/skin_graph/skin_graph_samples.human.sqlite`.
It holds isolated, edge, bent-chain, three-edge branch, missing-root and human
samples. Options use serde JSON **inside SQLite**; there is no competing JSON
project-file format. SQLite is native persistence; a future browser host must
provide storage separately without importing this crate into the core.
