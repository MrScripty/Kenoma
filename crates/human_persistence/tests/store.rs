use human_core::*;
use human_persistence::*;
use rusqlite::Connection;
use std::sync::atomic::{AtomicU64, Ordering};
static NEXT: AtomicU64 = AtomicU64::new(0);
struct TestFile(std::path::PathBuf);
impl TestFile {
    fn new() -> Self {
        Self(std::env::temp_dir().join(format!(
            "kenoma-graph-{}-{}.human.sqlite",
            std::process::id(),
            NEXT.fetch_add(1, Ordering::Relaxed)
        )))
    }
}
impl Drop for TestFile {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.0);
    }
}
#[test]
fn all_samples_round_trip_source_and_generated_geometry() -> Result<(), Box<dyn std::error::Error>>
{
    let mut store = HumanProjectStore::in_memory()?;
    for (name, graph) in sample_graphs() {
        let options = SkinGraphGenerateOptions::default();
        let id = save_skin_graph_to_project(&mut store, None, name, &graph, &options)?;
        let loaded = load_skin_graph_from_project(&store, id)?;
        assert_eq!(loaded.name, name);
        assert_eq!(loaded.graph, graph);
        assert_eq!(loaded.options, options);
        assert_eq!(
            generate_skin_graph_mesh(&graph, &options)?,
            generate_skin_graph_mesh(&loaded.graph, &loaded.options)?
        );
    }
    Ok(())
}
#[test]
fn save_update_and_failure_preserve_existing_source() -> Result<(), Box<dyn std::error::Error>> {
    let mut store = HumanProjectStore::in_memory()?;
    let mut graph = mannequin();
    let options = SkinGraphGenerateOptions::default();
    let id = save_skin_graph_to_project(&mut store, None, "human", &graph, &options)?;
    apply_graph_command(
        &mut graph,
        &GraphCommand::RotateBranch {
            pivot: 4,
            child: 5,
            axis: Vec3::Z,
            radians: 0.5,
        },
    )?;
    assert_eq!(
        save_skin_graph_to_project(&mut store, Some(id), "posed", &graph, &options)?,
        id
    );
    let good = graph.clone();
    graph.edges.push(SkinEdge { a: 0, b: 9999 });
    assert!(save_skin_graph_to_project(&mut store, Some(id), "bad", &graph, &options).is_err());
    let loaded = load_skin_graph_from_project(&store, id)?;
    assert_eq!(loaded.graph, good);
    assert_eq!(loaded.name, "posed");
    Ok(())
}
#[test]
fn future_versions_are_not_overwritten() -> Result<(), Box<dyn std::error::Error>> {
    let path = TestFile::new();
    let mut store = HumanProjectStore::open(&path.0)?;
    let id = save_skin_graph_to_project(
        &mut store,
        None,
        "future",
        &mannequin(),
        &Default::default(),
    )?;
    let raw = Connection::open(&path.0)?;
    raw.execute("UPDATE skin_graphs SET version=2 WHERE id=?1", [id])?;
    assert!(matches!(
        load_skin_graph_from_project(&store, id),
        Err(StoreError::Version)
    ));
    assert!(matches!(
        save_skin_graph_to_project(
            &mut store,
            Some(id),
            "overwrite",
            &SkinGraph::default(),
            &Default::default()
        ),
        Err(StoreError::Version)
    ));
    let count: i64 = raw.query_row(
        "SELECT COUNT(*) FROM skin_graph_nodes WHERE graph_id=?1",
        [id],
        |r| r.get(0),
    )?;
    assert_eq!(count, 16);
    raw.execute("UPDATE skin_graph_schema SET version=2", [])?;
    assert!(matches!(
        HumanProjectStore::open(&path.0),
        Err(StoreError::Version)
    ));
    Ok(())
}
#[test]
fn malformed_rows_fail_and_unrelated_tables_survive() -> Result<(), Box<dyn std::error::Error>> {
    let path = TestFile::new();
    let raw = Connection::open(&path.0)?;
    raw.execute_batch(
        "CREATE TABLE unrelated(value TEXT); INSERT INTO unrelated VALUES('untouched');",
    )?;
    let mut store = HumanProjectStore::open(&path.0)?;
    let id =
        save_skin_graph_to_project(&mut store, None, "human", &mannequin(), &Default::default())?;
    raw.execute(
        "UPDATE skin_graph_nodes SET flags=8 WHERE graph_id=?1 AND node_index=0",
        [id],
    )?;
    assert!(matches!(
        load_skin_graph_from_project(&store, id),
        Err(StoreError::CorruptRecord)
    ));
    raw.execute(
        "UPDATE skin_graph_nodes SET flags=1,node_index=99 WHERE graph_id=?1 AND node_index=0",
        [id],
    )?;
    assert!(matches!(
        load_skin_graph_from_project(&store, id),
        Err(StoreError::CorruptRecord)
    ));
    let value: String = raw.query_row("SELECT value FROM unrelated", [], |r| r.get(0))?;
    assert_eq!(value, "untouched");
    Ok(())
}
#[test]
fn concurrent_atomic_saves_load_consistent_snapshots() -> Result<(), Box<dyn std::error::Error>> {
    let path = TestFile::new();
    let mut store = HumanProjectStore::open(&path.0)?;
    let id = save_skin_graph_to_project(&mut store, None, "a", &mannequin(), &Default::default())?;
    let db_path = path.0.clone();
    let writer = std::thread::spawn(move || -> Result<(), StoreError> {
        let mut store = HumanProjectStore::open(db_path)?;
        for i in 0..30 {
            let mut graph = mannequin();
            let name = if i % 2 == 0 { "a" } else { "b" };
            if name == "b" {
                graph.nodes.pop();
                graph.edges.pop();
            }
            save_skin_graph_to_project(&mut store, Some(id), name, &graph, &Default::default())?;
        }
        Ok(())
    });
    for _ in 0..30 {
        let loaded = load_skin_graph_from_project(&store, id)?;
        assert_eq!(
            loaded.graph.nodes.len(),
            if loaded.name == "a" { 16 } else { 15 }
        );
    }
    writer.join().map_err(|_| "writer panicked")??;
    Ok(())
}
#[test]
fn committed_canonical_fixtures_regenerate_expected_meshes(
) -> Result<(), Box<dyn std::error::Error>> {
    let path = TestFile::new();
    std::fs::copy(
        concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../../assets/samples/skin_graph/skin_graph_samples.human.sqlite"
        ),
        &path.0,
    )?;
    let store = HumanProjectStore::open(&path.0)?;
    let counts = [
        (26, 48),
        (42, 80),
        (186, 352),
        (152, 288),
        (26, 48),
        (820, 1536),
    ];
    for (index, ((name, source), (vertices, triangles))) in
        sample_graphs().into_iter().zip(counts).enumerate()
    {
        let loaded = load_skin_graph_from_project(&store, index as i64 + 1)?;
        assert_eq!(loaded.name, name);
        assert_eq!(loaded.graph, source);
        let mesh = generate_skin_graph_mesh(&loaded.graph, &loaded.options)?;
        assert_eq!(
            (mesh.positions.len(), mesh.indices.len() / 3),
            (vertices, triangles)
        );
    }
    Ok(())
}
#[test]
fn sql_failure_mid_save_rolls_back_metadata_and_source() -> Result<(), Box<dyn std::error::Error>> {
    let path = TestFile::new();
    let mut store = HumanProjectStore::open(&path.0)?;
    let original = mannequin();
    let id =
        save_skin_graph_to_project(&mut store, None, "original", &original, &Default::default())?;
    let raw = Connection::open(&path.0)?;
    raw.execute_batch("CREATE TRIGGER fail_insert BEFORE INSERT ON skin_graph_edges BEGIN SELECT RAISE(ABORT,'test failure'); END;")?;
    let mut changed = original.clone();
    apply_graph_command(
        &mut changed,
        &GraphCommand::MoveNode {
            node: 6,
            position: Vec3::ONE,
        },
    )?;
    assert!(save_skin_graph_to_project(
        &mut store,
        Some(id),
        "changed",
        &changed,
        &Default::default()
    )
    .is_err());
    let loaded = load_skin_graph_from_project(&store, id)?;
    assert_eq!(loaded.name, "original");
    assert_eq!(loaded.graph, original);
    Ok(())
}
