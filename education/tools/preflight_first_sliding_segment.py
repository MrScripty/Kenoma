#!/usr/bin/env python3
"""Executable field/custody/rollback checks; no ODE steps or accepted entry."""
import hashlib
import itertools
import json
import numpy as np
from first_sliding_segment_engine import (ROOT,DATA,PREP,SegmentEngine,Source,Failure,
    verify_bindings,dump_new,native_field,independent_field,compare_rows,decode_reduced)
from first_sliding_segment_preflight import custody
from run_ordinary_crossing_consistency import replay_dense


def field_equivalence(engine):
    z=np.array(engine.candidate['state']);cfg=engine.cfg
    reduced=np.r_[z[:4],z[5:]];decoded=decode_reduced(reduced,cfg)
    source=Source()
    try:
        native,nr=native_field(z,cfg,source,True)
        independent,rr=independent_field(decoded,cfg,True)
        difference=nr-rr
        if max(abs(difference))>1e-8:raise Failure('preflight-RHS-equivalence','Additional unchanged-rate diagnostic failed')
        # Differentiate I=B-ub-.4*(target-FT)/100 with independent tendon slope.
        decoded_Idot=-.4*independent['kt']/100*(rr[0]+.1*rr[3])
        tangent=abs(independent['d']+nr[4]);normal=max(abs(native['normal_on']-independent['normal_on']),abs(native['normal_off']-independent['normal_off']))
        if max(tangent,normal,abs(decoded_Idot-rr[4]))>1e-8:
            raise Failure('preflight-tangency','Field/decoded normal or derivative identity failed')
        if not np.array_equal(np.r_[z[:4],z[5:]],np.r_[decoded[:4],decoded[5:]]):
            raise Failure('preflight-decode','Other ten coordinates differ')
        if abs(decoded[4]-z[4])>1e-9:raise Failure('preflight-coordinate','Finite I reconstruction exceeds original gate')
        fingerprint=engine.fingerprint()
        J=engine.jac(engine.candidate['t'],reduced if engine.rep=='reduced-independent' else z)
        first_ledger=4 if engine.rep=='reduced-independent' else 5
        if not np.array_equal(J[:,first_ledger:],np.zeros_like(J[:,first_ledger:])) or engine.fingerprint()!=fingerprint:
            raise Failure('preflight-Jacobian','Auxiliary Jacobian changed ledger columns or accepted custody')
        return dict(passed=True,Jacobian_auxiliaries=engine.jacobian_probes,Jacobian_ledger_columns_exactly_zero=True,Jacobian_custody_unchanged=True,native_full_rate=nr.tolist(),independent_lifted_rate=rr.tolist(),
                    native_full_dimension=11,reduced_dimension=10,difference=difference.tolist(),
                    max_abs_RHS_difference=float(max(abs(difference))),additional_RHS_component_gate=1e-8,
                    decoded_Idot=decoded_Idot,independent_Idot=rr[4],
                    tangent_residual_per_s=tangent,normal_disagreement_per_s=normal,
                    other_ten_bitwise_preserved=True,signed_I_reconstruction=float(decoded[4]-z[4]),
                    native_H=native['H'],decoded_H=independent['H'],theta=native['theta'],
                    normal_on=native['normal_on'],normal_off=native['normal_off'],accepted=False)
    finally:source.close()


def runtime_entry_checks(engines,proposals):
    keys=list(engines);times=[float(k*.001) for k in range(263)]
    maps={key:engines[key].history+proposals[key]['prefix']['rows'] for key in keys}
    comparisons={a+' vs '+b:compare_rows(maps[a],maps[b],times) for a,b in itertools.combinations(keys,2)}
    event_orders=[[e['type'] for e in engines[key].events] for key in keys]
    exact_order=['activation-equality','ordinary-outward','ordinary-inward']
    event_spans={kind:max(next(e['t'] for e in engines[key].events if e['type']==kind) for key in keys)-min(next(e['t'] for e in engines[key].events if e['type']==kind) for key in keys) for kind in exact_order}
    candidate_times={key:engines[key].candidate['t'] for key in keys}
    candidate_span=max(candidate_times.values())-min(candidate_times.values())
    passed=len(keys)==12 and len(comparisons)==66 and all(c['passed'] for c in comparisons.values()) and all(o==exact_order for o in event_orders) and max(event_spans.values())<=2e-6 and candidate_span<=2e-6
    return dict(passed=passed,required_cells=12,required_pairs=66,cells=len(keys),pairs=len(comparisons),
                original_grid_times=times,comparisons=comparisons,event_order_valid=all(o==exact_order for o in event_orders),
                prior_event_time_spans_s=event_spans,attracting_time_span_s=candidate_span,
                candidate_times=candidate_times,event_gate_s=2e-6,all_entries_unaccepted=all(not e.candidate['accepted'] for e in engines.values()))


def prepare_all(use_preflight=False):
    p=verify_bindings();engines={};proposals={};records={}
    stored=json.loads((DATA/'preflight/entry-preflight.json').read_text()) if use_preflight else None
    try:
        for key,path in p['entry_inputs'].items():
            incoming=json.loads((ROOT/path).read_text())
            prepared=stored['entries'][key]['preparation'] if stored else custody(ROOT/path,{})
            if not prepared.get('refined_admissibility',{}).get('prospectively_admissible'):
                raise Failure('entry-custody','Fresh own incoming root did not pass original gates')
            engine=SegmentEngine(incoming,prepared);engines[key]=engine
            proposal=engine.prepare_entry()
            proposal['sliding_entry_row']=engine.row(engine.candidate['t'],proposal['sliding_x'],'sliding')
            proposals[key]=proposal
            records[key]=dict(preparation=prepared,handoff=proposal['handoff'],field_equivalence=field_equivalence(engine),
                              prefix_guard_samples=proposal['prefix']['interval']['guard_samples'],
                              prefix_quadrature=proposal['prefix']['quad'].tolist(),accepted=False)
            if not use_preflight:
                fingerprint=engine.fingerprint();bad_calls=[0]
                def invalid_dense(t):
                    bad_calls[0]+=1
                    z=replay_dense(engine.incoming_dense,t)
                    if bad_calls[0]>=2:z[3]=.4
                    return z
                try:
                    engine.prepare_interval(engine.candidate['t'],np.array(engine.candidate['state']),invalid_dense,engine.incoming_dense,'incoming')
                except Failure as error:
                    rollback=dict(passed=engine.fingerprint()==fingerprint,rejected_code=error.code,
                                  validated_probe_calls=bad_calls[0],accepted_state_time_history_quadrature_unchanged=engine.fingerprint()==fingerprint,
                                  failed_probes=engine.probes[-1:],accepted=False)
                else:raise Failure('preflight-rollback','Deliberately invalid physical probe was accepted')
                if not rollback['passed']:raise Failure('preflight-rollback','Accepted custody changed after failed validation')
                records[key]['rollback']=rollback
                engine.probes=[]
            print('ENTRY CHECK',key,'root',engine.candidate['t'],'I/raw',proposal['handoff']['signed_delta_I'],proposal['handoff']['signed_delta_raw'],'unaccepted',flush=True)
        checks=runtime_entry_checks(engines,proposals)
        if not checks['passed']:raise Failure('entry-matrix-block','Common-time twelve-cell pre-entry checks failed')
        return engines,proposals,dict(passed=True,entries=records,common_checks=checks,
                                      ODE_steps_executed=0,accepted_entry_states=0,
                                      protocol_sha256=hashlib.sha256((DATA/'protocol.json').read_bytes()).hexdigest(),
                                      source_sha256=p['source_sha256'])
    except BaseException as error:
        error.entry_context=dict(entries=records,engines={key:engine.result() for key,engine in engines.items()},accepted_entries=0)
        for engine in engines.values():engine.close()
        raise


def main():
    engines={}
    try:
        engines,proposals,receipt=prepare_all()
        dump_new(DATA/'preflight/entry-preflight.json',receipt)
        print('PASS 12 field/custody/tangency/decoding/rollback checks; 66 comparisons on 263 absolute incoming grid times; ZERO accepted entries or ODE steps',flush=True)
    except BaseException as error:
        dump_new(DATA/'preflight/entry-preflight-failure.json',dict(passed=False,type=type(error).__name__,message=str(error),code=getattr(error,'code',None),accepted_entries=0,context=getattr(error,'entry_context',None)))
        raise
    finally:
        for engine in engines.values():engine.close()


if __name__=='__main__':main()
