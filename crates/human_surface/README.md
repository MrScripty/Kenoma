# Independent connected mannequin surface

Pure headless, deterministic Rust surface generation for the canonical 16-node
mannequin. No research imports, forces, simulation, renderer or persistence.
`generate_mannequin_surface(graph, head, options)` returns ordinary indexed
`GeneratedSkinMesh` buffers without modifying the graph. Errors are typed.

Limb capsule radii use smoothstep interpolation, whose zero endpoint derivatives
avoid shading creases where tapers meet round caps. Capsules are smoothly united with the torso and neck. The head is
part of the same implicit field: cranial, forehead, lower-face and chin volumes
produce a directional rounded human-like silhouette without cartoon facial
features. Head yaw then local pitch uses YXZ orientation around graph node 3;
+Y is up and +Z is forward. The head is deliberately schematic, not anatomical.

A conforming six-tetrahedra-per-cell extraction welds every crossed grid edge.
Gradient normals smooth the visible surface. Default cell size is 0.016 metres;
valid sizes are 0.008–0.04, additionally limited to 70% of the smallest radius.
Grid sampling is bounded to two million points and output to 300,000 vertices.
Too-large domains or too-fine resolution return an explicit resource error.

Topology and vertex counts change with pose and resolution. Source graph IDs
remain stable; generated surface IDs do not. Vertex order is deterministic for
identical inputs, including head orientation. Provenance identifies nearby source
edges or head node 3 and is approximate at blended joints. Radii are circularized
using the smaller source radius; this first surface adapter is mannequin-only.

At practical resolution the canonical pose and tested bent poses yield one
closed orientable vertex-manifold surface. Self-contact intentionally fuses nearby
limbs in the smooth union. This can create handles and changing topology, and is
not collision handling or a deformation mesh suitable for stable vertex caches.
Resolution is a quality/performance tradeoff, not an anatomical precision claim.

Supported source radii are 0.02–0.4 metres; canonical topology and the pelvis root
are required. The fixed-size head does not scale from the head node's radius.
Grid budgets can reject the finest allowed cell size on large domains.

Native release measurements in this workspace: the neutral default generates
46,728 vertices and 93,452 triangles in approximately 0.19 seconds in the final
smooth-taper run. Earlier equivalent-resolution runs under concurrent
browser/build/test load ranged up to 0.71 seconds. These measurements
are not browser latency claims. Browser JSON transfer and rendering add cost.
An explicit coarser cell size reduces both extraction work and geometric detail;
there is no silent quality reduction during dragging.
