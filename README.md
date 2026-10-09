# Kenoma
Experimental repo for human mesh generation to use as image diffusion reference in the whip project. On sucessful implementation it will be merged into the 3D tools in Pentimento along with diffusion support via Pantograph. 

This repo contains 3 main tracks:
1. A skinning tool that allows maniquins to be made from just a few connected vertices
2. A morph target system that aproximates real human anatomy
3. A biomechanical simulation for acurate anatomical features when posing

In theory the simpilist option is probably good enough for the intended use case, but morph targets have the potential for more control and consistent character generation. At this time i dont know if biomechanical simulation is practical as its much more difficult to create a system capable of acuratly simulating human anatomy and doing so in real time, but the problem is interesting enough i want to try it.

The word Kenoma comes from the ancient Greek word κένωμα which litteraly means "emptiness", "void", or "That which has been emptied". It seemed fitting for a lifeless mannequin that doesnt appear alive until diffusion paints it with life. 

## Independent simple posing tools

The [simple posing editor](browser/simple-graph/README.md) provides multiple
characters, scene gizmos, two-bone IK, head orientation, colors and undo/redo in
an embeddable static WebGL/WASM page. The headless `human_core` graph/edit API,
`human_persistence` SQLite store, `human_surface` connected mannequin generator
and `human_rig` stable pose deformation
are separate from the biomechanics research. See the [implementation inventory
and ownership boundary](docs/adr/001-simple-graph-boundary.md) and
[connected surface contract](crates/human_surface/README.md). This is schematic
posing and mesh generation, with no anatomical accuracy or physical simulation.

## Educational mechanics book

The additive [educational book and seven 3D laboratories](education/README.md) develop force, torque, energy, activation/release, tendon storage, a worked spatial FEM/fast-solver comparison and a spatial muscle-under-skin/elbow-contact capstone at identical poses. Licensed atlas surfaces, recorded normalized human signals and source model parameters remain separate evidence streams. The book includes original numerical experiments, primary citations and visible checked Lean claims. Its schematic one-way capstone is an educational model; the original production simulator plans remain separate.
