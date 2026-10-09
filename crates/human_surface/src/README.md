# Surface implementation

`lib.rs` owns the entire independent mannequin surface adapter. Public input
validation constructs tapered capsules and a rotated head field. A bounded grid
samples their smooth union, then a conforming six-tetrahedron split extracts one
indexed surface using a shared lattice-edge cache. Central field differences
supply unit normals; source attribution is approximate near smooth blends.

Exact/near-zero scalar samples use one positive tie rule. Interpolation keeps a
small clearance from lattice endpoints, avoiding duplicate f32 positions without
skipping triangles or opening holes. Dynamic array indexing is locally allowed
because indices come from validated topology, fixed tetrahedra and checked grid
sizes; invalid geometry fails with a typed error.

Field primitive culling uses conservative lower bounds and is checked against
unculled samples in unit tests. Integration tests in `../tests/surface.rs` verify
edge incidence, winding, vertex-link cycles, connected components, geometric
validity, normal orientation, pose extremes and determinism. No simulation,
rendering, scene-state or persistence responsibility belongs in this directory.
