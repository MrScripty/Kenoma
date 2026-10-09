use human_core::*;
use human_persistence::*;
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = std::env::args()
        .nth(1)
        .ok_or("usage: samples <new-file.human.sqlite>")?;
    // Never silently overwrite or append to an existing project.
    let _file = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&path)?;
    let mut store = HumanProjectStore::open(path)?;
    for (name, graph) in sample_graphs() {
        let options = SkinGraphGenerateOptions::default();
        let id = save_skin_graph_to_project(&mut store, None, name, &graph, &options)?;
        let saved = load_skin_graph_from_project(&store, id)?;
        let mesh = generate_skin_graph_mesh(&saved.graph, &saved.options)?;
        println!(
            "{id}: {name}: {} nodes, {} edges -> {} vertices, {} triangles",
            graph.nodes.len(),
            graph.edges.len(),
            mesh.positions.len(),
            mesh.indices.len() / 3
        );
    }
    Ok(())
}
