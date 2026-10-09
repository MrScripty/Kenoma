use human_core::*;
use human_wasm::evaluate;
use serde_json::{json, Value};
fn call(value: Value) -> Result<Value, serde_json::Error> {
    serde_json::from_str(&evaluate(&value.to_string()))
}
#[test]
fn sample_and_pose_match_native_core() -> Result<(), Box<dyn std::error::Error>> {
    let sample = call(json!({"version":1,"operation":{"type":"mannequin"}}))?;
    assert_eq!(sample.get("ok"), Some(&json!(true)));
    let graph: SkinGraph =
        serde_json::from_value(sample.get("graph").ok_or("missing graph")?.clone())?;
    assert_eq!(graph, mannequin());
    let generated: GeneratedSkinMesh =
        serde_json::from_value(sample.get("mesh").ok_or("missing mesh")?.clone())?;
    assert_eq!(
        generated,
        generate_skin_graph_mesh(&graph, &Default::default())?
    );
    let command = GraphCommand::RotateBranch {
        pivot: 4,
        child: 5,
        axis: Vec3::Z,
        radians: 0.8,
    };
    let response =
        call(json!({"version":1,"operation":{"type":"edit","graph":graph,"commands":[command]}}))?;
    let mut expected = graph;
    apply_graph_command(&mut expected, &command)?;
    let actual: SkinGraph =
        serde_json::from_value(response.get("graph").ok_or("missing graph")?.clone())?;
    assert_eq!(actual, expected);
    assert_eq!(
        evaluate(&json!({"version":1,"operation":{"type":"generate","graph":actual}}).to_string()),
        evaluate(
            &json!({"version":1,"operation":{"type":"generate","graph":expected}}).to_string()
        )
    );
    Ok(())
}
#[test]
fn malformed_versions_invalid_graphs_and_failed_batches_are_structured(
) -> Result<(), Box<dyn std::error::Error>> {
    for (request, code) in [
        (
            json!({"version":2,"operation":{"type":"mannequin"}}),
            "unsupported_version",
        ),
        (
            json!({"version":1,"operation":{"type":"unknown"}}),
            "invalid_request",
        ),
        (
            json!({"version":1,"extra":true,"operation":{"type":"mannequin"}}),
            "invalid_request",
        ),
        (
            json!({"version":1,"operation":{"type":"edit","graph":mannequin(),"commands":[{"MoveNode":{"node":5,"position":[0,1,0]}},{"DeleteNode":{"node":999}}]}}),
            "invalid_node",
        ),
        (
            json!({"version":1,"operation":{"type":"generate","graph":mannequin(),"options":{"ring_sides":8,"target_segment_length_factor":0,"max_edge_segments":64}}}),
            "invalid_options",
        ),
    ] {
        let response = call(request)?;
        assert_eq!(response.pointer("/error/code"), Some(&json!(code)));
        assert_eq!(response.get("ok"), Some(&json!(false)));
        assert!(response.get("graph").is_none());
    }
    let oversized = evaluate(&" ".repeat(human_wasm::MAX_REQUEST_BYTES + 1));
    assert_eq!(
        serde_json::from_str::<Value>(&oversized)?.pointer("/error/code"),
        Some(&json!("resource_limit"))
    );
    assert_eq!(
        serde_json::from_str::<Value>(&evaluate("{"))?.pointer("/error/code"),
        Some(&json!("invalid_request"))
    );
    Ok(())
}
#[test]
fn portable_u32_counts_and_command_limit() -> Result<(), Box<dyn std::error::Error>> {
    for count in [
        serde_json::json!(4294967296_u64),
        serde_json::json!(-1),
        serde_json::json!(8.5),
    ] {
        let response = call(
            json!({"version":1,"operation":{"type":"generate","graph":mannequin(),"options":{"ring_sides":count,"target_segment_length_factor":1.25,"max_edge_segments":64}}}),
        )?;
        assert_eq!(
            response.pointer("/error/code"),
            Some(&json!("invalid_request"))
        );
    }
    let commands = vec![json!({"MarkRoot":{"node":0}}); 129];
    let response = call(
        json!({"version":1,"operation":{"type":"edit","graph":mannequin(),"commands":commands}}),
    )?;
    assert_eq!(
        response.pointer("/error/code"),
        Some(&json!("resource_limit"))
    );
    Ok(())
}

#[test]
fn connected_surface_contract_matches_native() -> Result<(), Box<dyn std::error::Error>> {
    let graph = mannequin();
    let head = human_surface::HeadPose {
        yaw: 0.4,
        pitch: -0.2,
    };
    let options = human_surface::SurfaceOptions { cell_size: 0.028 };
    let response = call(
        json!({"version":1,"operation":{"type":"surface","graph":graph,"head":head,"surface_options":options}}),
    )?;
    assert_eq!(response.get("ok"), Some(&json!(true)));
    assert_eq!(
        serde_json::from_value::<human_surface::HeadPose>(
            response.get("head").ok_or("missing head")?.clone()
        )?,
        head
    );
    assert_eq!(
        serde_json::from_value::<human_surface::SurfaceOptions>(
            response
                .get("surface_options")
                .ok_or("missing surface options")?
                .clone()
        )?,
        options
    );
    let mesh: GeneratedSkinMesh =
        serde_json::from_value(response.get("mesh").ok_or("missing mesh")?.clone())?;
    assert_eq!(
        mesh,
        human_surface::generate_mannequin_surface(&graph, &head, &options)?
    );
    let bad = call(
        json!({"version":1,"operation":{"type":"surface","graph":graph,"surface_options":{"cell_size":0}}}),
    )?;
    assert_eq!(bad.pointer("/error/code"), Some(&json!("invalid_surface")));
    assert!(bad.get("mesh").is_none());
    Ok(())
}

#[test]
fn rig_handles_are_versioned_reusable_and_released() -> Result<(), Box<dyn std::error::Error>> {
    let bound = call(
        json!({"version":1,"operation":{"type":"rig_bind","rig_version":1,"surface_options":{"cell_size":0.028}}}),
    )?;
    assert_eq!(bound.get("ok"), Some(&json!(true)));
    let id = bound.get("rig_id").ok_or("missing rig_id")?;
    let mut graph = mannequin();
    apply_graph_command(
        &mut graph,
        &GraphCommand::RotateBranch {
            pivot: 4,
            child: 5,
            axis: Vec3::Y,
            radians: 1.2,
        },
    )?;
    let request = json!({"version":1,"operation":{"type":"rig_deform","rig_version":1,"rig_id":id,"graph":graph,"head":{"yaw":0.3,"pitch":0.1}}});
    let posed = call(request.clone())?;
    assert_eq!(posed.get("ok"), Some(&json!(true)));
    assert_eq!(
        posed.pointer("/mesh/indices"),
        bound.pointer("/mesh/indices")
    );
    assert_ne!(
        posed.pointer("/mesh/positions"),
        bound.pointer("/mesh/positions")
    );
    assert_eq!(posed, call(request.clone())?);
    let bad = call(
        json!({"version":1,"operation":{"type":"rig_deform","rig_version":2,"rig_id":id,"graph":graph}}),
    )?;
    assert_eq!(
        bad.pointer("/error/code"),
        Some(&json!("unsupported_rig_version"))
    );
    let mut malformed = graph.clone();
    malformed.edges.pop();
    let bad = call(
        json!({"version":1,"operation":{"type":"rig_deform","rig_version":1,"rig_id":id,"graph":malformed}}),
    )?;
    assert_eq!(bad.pointer("/error/code"), Some(&json!("invalid_rig")));
    assert_eq!(posed, call(request.clone())?);
    let released =
        call(json!({"version":1,"operation":{"type":"rig_release","rig_version":1,"rig_id":id}}))?;
    assert_eq!(released.get("released"), Some(&json!(true)));
    assert_eq!(
        call(request)?.pointer("/error/code"),
        Some(&json!("unknown_rig"))
    );
    Ok(())
}

#[test]
fn rig_registry_budget_and_monotonic_ids() -> Result<(), Box<dyn std::error::Error>> {
    let mut ids = Vec::new();
    for _ in 0..16 {
        let r = call(
            json!({"version":1,"operation":{"type":"rig_bind","rig_version":1,"surface_options":{"cell_size":0.028}}}),
        )?;
        assert_eq!(r.get("ok"), Some(&json!(true)));
        ids.push(
            r.get("rig_id")
                .and_then(Value::as_u64)
                .ok_or("missing id")?,
        );
    }
    let denied = call(json!({"version":1,"operation":{"type":"rig_bind","rig_version":1}}))?;
    assert_eq!(
        denied.pointer("/error/code"),
        Some(&json!("resource_limit"))
    );
    for id in &ids {
        assert_eq!(
            call(
                json!({"version":1,"operation":{"type":"rig_release","rig_version":1,"rig_id":id}})
            )?
            .get("ok"),
            Some(&json!(true))
        );
    }
    let r = call(
        json!({"version":1,"operation":{"type":"rig_bind","rig_version":1,"surface_options":{"cell_size":0.028}}}),
    )?;
    let id = r
        .get("rig_id")
        .and_then(Value::as_u64)
        .ok_or("missing id")?;
    assert!(ids.iter().all(|old| id > *old));
    call(json!({"version":1,"operation":{"type":"rig_release","rig_version":1,"rig_id":id}}))?;
    Ok(())
}
