#!/usr/bin/env python3
"""Pure structural checks only; no candidate mechanical trajectory."""
import sys,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from combined_incoming_preflight import P,decide_trial,staged_restart

def event(kind,**kwargs):return dict(kind=kind,bracket=[.1,.100000000001],**kwargs)

class Checks(unittest.TestCase):
    def test_execution_hold_is_explicit(self):self.assertFalse(P['candidate_matrix_execution_authorized']);self.assertEqual(P['activation_review_disposition'],'pending')
    def test_equality_prefix_changes_only_activation_branch(self):
        r=decide_trial([event('activation-equality',interior=True,transverse=True)],'integrating','activation');self.assertTrue(r['advance']);self.assertEqual(r['controller'],'integrating');self.assertEqual(r['activation'],'deactivation');self.assertTrue(r['preserve_original_rk_trial_end'])
    def test_outward_then_inward_retain_negative_activation(self):
        outward=event('ordinary-outward',same_direction_normals=True,g=-.02);r=decide_trial([outward],'integrating','deactivation');self.assertEqual(r['controller'],'frozen');self.assertEqual(r['activation'],'deactivation');self.assertFalse(r['preserve_original_rk_trial_end'])
        r=decide_trial([event('ordinary-inward',same_direction_normals=True,g=-.002)],'frozen','deactivation');self.assertEqual(r['controller'],'integrating');self.assertEqual(r['activation'],'deactivation')
    def test_attracting_event_never_advances(self):
        r=decide_trial([event('attracting')],'integrating','deactivation');self.assertEqual(r['decision'],'hold');self.assertFalse(r['advance'])
    def test_overlapping_event_order_stops(self):
        events=[event('activation-equality',interior=True,transverse=True),event('ordinary-outward',same_direction_normals=True,g=-.02)]
        r=decide_trial(events,'integrating','activation');self.assertEqual(r['reason'],'unresolved-event-order');self.assertFalse(r['advance'])
    def test_earliest_independent_event_accepted_later_suffix_discarded(self):
        events=[dict(kind='ordinary-outward',bracket=[.1001,.100100000001],same_direction_normals=True,g=-.02),event('activation-equality',interior=True,transverse=True)]
        r=decide_trial(events,'integrating','activation');self.assertEqual(r['decision'],'activation-prefix');self.assertEqual(r['discarded_later_candidates'],['ordinary-outward']);self.assertTrue(r['advance'])
    def test_later_auxiliary_activation_candidate_is_recomputed_after_controller(self):
        events=[dict(kind='activation-equality',bracket=[.1001,.100100000001],interior=True,transverse=True),event('ordinary-inward',same_direction_normals=True,g=-.002)]
        r=decide_trial(events,'frozen','deactivation');self.assertEqual(r['decision'],'ordinary-prefix');self.assertEqual(r['discarded_later_candidates'],['activation-equality']);self.assertEqual(r['controller'],'integrating')
    def test_activation_tangency_or_noninterior_equality_stops(self):
        for interior,transverse in [(False,True),(True,False)]:
            r=decide_trial([event('activation-equality',interior=interior,transverse=transverse)],'integrating','activation');self.assertEqual(r['reason'],'uncertified-activation-crossing');self.assertFalse(r['advance'])
    def test_earliest_actual_activation_recrossing_stops(self):
        r=decide_trial([event('activation-equality',interior=True,transverse=True)],'integrating','deactivation');self.assertEqual(r['reason'],'unexpected-activation-crossing');self.assertFalse(r['advance'])
    def test_command_root_coincidence_has_no_guessed_priority(self):
        r=decide_trial([event('activation-equality',interior=True,transverse=True)],'integrating','activation',command_time=.1);self.assertEqual(r['reason'],'compound-command-root');self.assertFalse(r['advance'])
    def test_controller_cut_carries_pending_activation_remainder(self):
        r=decide_trial([event('ordinary-outward',same_direction_normals=True,g=-.02)],'integrating','deactivation',remainder_end=.1002);self.assertTrue(r['advance']);self.assertTrue(r['preserve_original_rk_trial_end']);self.assertEqual(r['pending_activation_remainder_end'],.1002)
    def test_controller_equality_implies_bound_activation_not_interior(self):
        for B in [.01,1.]:
            a=B;u=max(.01,min(1.,B));self.assertEqual(u-a,0);self.assertFalse(.01<u<1.)
        r=decide_trial([event('ordinary-outward',same_direction_normals=True,g=0)],'integrating','deactivation');self.assertEqual(r['reason'],'activation-side-ambiguity-at-controller-crossing')
    def test_restart_copies_all_eleven_event_coordinates(self):
        previous=dict(time=0.,state=tuple(range(11)),controller='integrating',activation='activation');original=copy.deepcopy(previous);candidate=dict(time=.1,state=tuple(x+.125 for x in range(11)));decision=decide_trial([event('activation-equality',interior=True,transverse=True)],'integrating','activation');r=staged_restart(previous,candidate,decision,lambda c:True)
        self.assertEqual(r['state'],candidate['state']);self.assertEqual(previous,original);self.assertTrue(r['new_solver_required'])
    def test_failed_or_held_prefix_does_not_advance_any_coordinate(self):
        previous=dict(time=0.,state=tuple(range(11)),controller='integrating',activation='activation');original=copy.deepcopy(previous);candidate=dict(time=.1,state=tuple(x+.125 for x in range(11)));d=decide_trial([event('activation-equality',interior=True,transverse=True)],'integrating','activation');self.assertEqual(staged_restart(previous,candidate,d,lambda c:False),previous)
        held=decide_trial([event('attracting')],'integrating','activation');self.assertEqual(staged_restart(previous,candidate,held,lambda c:True),previous);self.assertEqual(previous,original)

if __name__=='__main__':unittest.main(verbosity=2)
