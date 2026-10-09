//! SQLite adapter for the independent procedural graph system.
use human_core::*;
use rusqlite::{params, Connection};
use std::path::Path;

pub type SkinGraphId = i64;
#[derive(Debug, thiserror::Error)]
pub enum StoreError {
    #[error(transparent)]
    Sql(#[from] rusqlite::Error),
    #[error(transparent)]
    Graph(#[from] GraphError),
    #[error(transparent)]
    Options(#[from] serde_json::Error),
    #[error("unsupported skin graph schema or record version")]
    Version,
    #[error("noncanonical node or edge ordering, flags, or identifier")]
    CorruptRecord,
}
pub struct HumanProjectStore {
    connection: Connection,
}
#[derive(Clone, Debug)]
pub struct StoredSkinGraph {
    pub id: SkinGraphId,
    pub name: String,
    pub graph: SkinGraph,
    pub options: SkinGraphGenerateOptions,
}
impl HumanProjectStore {
    pub fn open(path: impl AsRef<Path>) -> Result<Self, StoreError> {
        Self::initialize(Connection::open(path)?)
    }
    pub fn in_memory() -> Result<Self, StoreError> {
        Self::initialize(Connection::open_in_memory()?)
    }
    fn initialize(mut connection: Connection) -> Result<Self, StoreError> {
        connection.execute_batch("PRAGMA foreign_keys=ON;")?;
        let tx = connection.transaction()?;
        tx.execute_batch("CREATE TABLE IF NOT EXISTS skin_graph_schema (id INTEGER PRIMARY KEY CHECK(id=1), version INTEGER NOT NULL);
            INSERT OR IGNORE INTO skin_graph_schema VALUES(1,1);")?;
        let version: i64 = tx.query_row(
            "SELECT version FROM skin_graph_schema WHERE id=1",
            [],
            |r| r.get(0),
        )?;
        if version != 1 {
            return Err(StoreError::Version);
        }
        tx.execute_batch("CREATE TABLE IF NOT EXISTS skin_graphs (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, version INTEGER NOT NULL,
            generation_options_blob TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS skin_graph_nodes (
            graph_id INTEGER NOT NULL REFERENCES skin_graphs(id) ON DELETE CASCADE,
            node_index INTEGER NOT NULL, position_x_m REAL NOT NULL, position_y_m REAL NOT NULL,
            position_z_m REAL NOT NULL, radius_x_m REAL NOT NULL, radius_y_m REAL NOT NULL,
            flags INTEGER NOT NULL, PRIMARY KEY(graph_id,node_index));
            CREATE TABLE IF NOT EXISTS skin_graph_edges (
            graph_id INTEGER NOT NULL REFERENCES skin_graphs(id) ON DELETE CASCADE,
            edge_index INTEGER NOT NULL, node_a INTEGER NOT NULL, node_b INTEGER NOT NULL,
            PRIMARY KEY(graph_id,edge_index));")?;
        tx.commit()?;
        Ok(Self { connection })
    }
}
/// Save source atomically. `None` allocates an ID; `Some` updates an existing ID.
/// Geometry is validated for these options but never stored in the database.
pub fn save_skin_graph_to_project(
    project: &mut HumanProjectStore,
    id: Option<SkinGraphId>,
    name: &str,
    graph: &SkinGraph,
    options: &SkinGraphGenerateOptions,
) -> Result<SkinGraphId, StoreError> {
    generate_skin_graph_mesh(graph, options)?;
    let encoded = serde_json::to_string(options)?;
    let tx = project.connection.transaction()?;
    let id = if let Some(id) = id {
        let version: i64 =
            tx.query_row("SELECT version FROM skin_graphs WHERE id=?1", [id], |r| {
                r.get(0)
            })?;
        if version != 1 {
            return Err(StoreError::Version);
        }
        if tx.execute("UPDATE skin_graphs SET name=?1, generation_options_blob=?2, updated_at=CURRENT_TIMESTAMP WHERE id=?3",params![name,encoded,id])? != 1 { return Err(StoreError::CorruptRecord); }
        tx.execute("DELETE FROM skin_graph_nodes WHERE graph_id=?1", [id])?;
        tx.execute("DELETE FROM skin_graph_edges WHERE graph_id=?1", [id])?;
        id
    } else {
        tx.execute(
            "INSERT INTO skin_graphs(name,version,generation_options_blob) VALUES(?1,1,?2)",
            params![name, encoded],
        )?;
        tx.last_insert_rowid()
    };
    for (index, node) in graph.nodes.iter().enumerate() {
        tx.execute(
            "INSERT INTO skin_graph_nodes VALUES(?1,?2,?3,?4,?5,?6,?7,?8)",
            params![
                id,
                index as i64,
                node.position.x,
                node.position.y,
                node.position.z,
                node.radii.x,
                node.radii.y,
                i32::from(node.root)
            ],
        )?;
    }
    for (index, edge) in graph.edges.iter().enumerate() {
        tx.execute(
            "INSERT INTO skin_graph_edges VALUES(?1,?2,?3,?4)",
            params![id, index as i64, edge.a as i64, edge.b as i64],
        )?;
    }
    tx.commit()?;
    Ok(id)
}
pub fn load_skin_graph_from_project(
    project: &HumanProjectStore,
    id: SkinGraphId,
) -> Result<StoredSkinGraph, StoreError> {
    let tx = project.connection.unchecked_transaction()?;
    let (name, version, encoded): (String, i64, String) = tx.query_row(
        "SELECT name,version,generation_options_blob FROM skin_graphs WHERE id=?1",
        [id],
        |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?)),
    )?;
    if version != 1 {
        return Err(StoreError::Version);
    }
    let options: SkinGraphGenerateOptions = serde_json::from_str(&encoded)?;
    let mut graph = SkinGraph::default();
    let mut statement = tx.prepare("SELECT node_index,position_x_m,position_y_m,position_z_m,radius_x_m,radius_y_m,flags FROM skin_graph_nodes WHERE graph_id=?1 ORDER BY node_index")?;
    let rows = statement.query_map([id], |r| {
        Ok((
            r.get::<_, u32>(0)? as usize,
            SkinNode {
                position: Vec3::new(r.get(1)?, r.get(2)?, r.get(3)?),
                radii: Vec2::new(r.get(4)?, r.get(5)?),
                root: r.get::<_, i64>(6)? == 1,
            },
            r.get::<_, i64>(6)?,
        ))
    })?;
    for row in rows {
        let (index, node, flags) = row?;
        if index != graph.nodes.len() || !(0..=1).contains(&flags) {
            return Err(StoreError::CorruptRecord);
        }
        if index >= MAX_NODES {
            return Err(GraphError::ResourceLimit.into());
        }
        graph.nodes.push(node);
    }
    let mut statement = tx.prepare("SELECT edge_index,node_a,node_b FROM skin_graph_edges WHERE graph_id=?1 ORDER BY edge_index")?;
    let rows = statement.query_map([id], |r| {
        Ok((
            r.get::<_, u32>(0)? as usize,
            SkinEdge {
                a: r.get::<_, u32>(1)? as usize,
                b: r.get::<_, u32>(2)? as usize,
            },
        ))
    })?;
    for row in rows {
        let (index, edge) = row?;
        if index != graph.edges.len() {
            return Err(StoreError::CorruptRecord);
        }
        if index >= MAX_EDGES {
            return Err(GraphError::ResourceLimit.into());
        }
        graph.edges.push(edge);
    }
    generate_skin_graph_mesh(&graph, &options)?;
    Ok(StoredSkinGraph {
        id,
        name,
        graph,
        options,
    })
}
