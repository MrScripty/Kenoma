"""Counterexamples to treating edge closure and zero crossings as clearance."""
import copy
import pathlib
import sys
import unittest

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / 'data/elbow-v1/scripts'
sys.path.insert(0, str(SCRIPTS))
import audit_arm_surface_quality as audit


class SurfaceQualityTests(unittest.TestCase):
    tetra_vertices = [[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]]
    tetra_faces = [[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]]

    def test_closed_tetrahedron(self):
        d = audit.topology(self.tetra_vertices, self.tetra_faces)
        self.assertTrue(d['closed_edge_manifold'])
        c = d['face_connected_components'][0]
        self.assertTrue(c['closed_vertex_manifold'])
        self.assertEqual(c['faces_requiring_orientation_change'], 0)
        self.assertAlmostEqual(c['component_relative_signed_volume_diagnostic_m3'], 1 / 6)

    def test_open_surface(self):
        d = audit.topology(self.tetra_vertices, self.tetra_faces[:-1])
        self.assertEqual(d['boundary_edges'], 3)
        self.assertFalse(d['closed_edge_manifold'])
        self.assertIsNone(d['face_connected_components'][0]['component_relative_signed_volume_diagnostic_m3'])

    def test_one_reversed_face(self):
        faces = copy.deepcopy(self.tetra_faces)
        faces[1].reverse()
        d = audit.topology(self.tetra_vertices, faces)
        self.assertEqual(d['same_direction_two_face_edges'], 3)
        self.assertEqual(d['face_connected_components'][0]['faces_requiring_orientation_change'], 1)

    def test_inward_shell(self):
        d = audit.topology(self.tetra_vertices, [list(reversed(t)) for t in self.tetra_faces])
        self.assertEqual(d['face_connected_components'][0]['faces_requiring_orientation_change'], 4)

    def test_two_coincident_triangles_are_not_volume(self):
        d = audit.topology(self.tetra_vertices[:3], [[0, 1, 2], [0, 2, 1]])
        self.assertTrue(d['closed_edge_manifold'])
        self.assertEqual(d['duplicate_triangle_excess'], 1)
        c = d['face_connected_components'][0]
        self.assertTrue(c['exact_zero_component_relative_volume'])
        self.assertEqual(c['coincident_triangle_source_face_groups'], [[0, 1]])

    def test_nonmanifold_edge(self):
        d = audit.topology(self.tetra_vertices, self.tetra_faces + [[0, 1, 2]])
        self.assertEqual(d['nonmanifold_edges'], 3)
        self.assertFalse(d['closed_edge_manifold'])

    def test_vertex_pinched_shells(self):
        vertices = self.tetra_vertices + [[-1., 0., 0.], [0., -1., 0.], [0., 0., -1.]]
        mapping = [0, 4, 5, 6]
        faces = self.tetra_faces + [[mapping[i] for i in t] for t in self.tetra_faces]
        d = audit.topology(vertices, faces)
        self.assertTrue(d['closed_edge_manifold'])
        self.assertEqual(d['nonmanifold_vertex_count'], 1)
        self.assertEqual(len(d['face_connected_components']), 2)

    def test_welding_is_exact_and_does_not_mutate(self):
        vertices = [[0., 0., 0.], [0., 0., 0.], [1e-15, 0., 0.]]
        original = copy.deepcopy(vertices)
        unique, faces, mapping = audit.exact_weld(vertices, [[0, 1, 2]])
        self.assertEqual(vertices, original)
        self.assertEqual(mapping, [0, 0, 1])
        self.assertEqual(len(unique), 2)

    def test_transverse_crossing(self):
        a = [[0., 0., 0.], [2., 0., 0.], [0., 2., 0.]]
        b = [[.5, .5, -1.], [.5, .5, 1.], [1.5, .5, 1.]]
        d = audit.transverse_pairs(a, [[0, 1, 2]], b, [[0, 1, 2]])
        self.assertEqual(d['transverse_crossing_triangle_pairs'], 1)
        self.assertEqual(d['full_self_intersection_clearance'], 'not_assessed')

    def test_coplanar_overlap_is_not_cleared(self):
        a = [[0., 0., 0.], [2., 0., 0.], [0., 2., 0.]]
        d = audit.transverse_pairs(a, [[0, 1, 2]], a, [[0, 1, 2]])
        self.assertEqual(d['transverse_crossing_triangle_pairs'], 0)
        self.assertEqual(d['full_self_intersection_clearance'], 'not_assessed')

    def test_source_landmark_identity_cannot_be_reordered(self):
        doc = {'landmarks': {'pick': {'element_id': 'test', 'triangle_zero_based': 0,
                                    'vertex_indices_zero_based': [0, 1, 2], 'barycentric': [.2, .3, .5],
                                    'atlas_position_m': [.3, .5, 0.], 'evidence_class': 'authored',
                                    'review_status': 'pending', 'uncertainty_radius_m': .003}}}
        part = {'vertices_m': self.tetra_vertices, 'triangles_zero_based': [[0, 1, 2]]}
        result = audit.validate_landmarks(doc, {'test': part})
        self.assertFalse(result[0]['uncertainty_is_measured'])
        part['triangles_zero_based'][0].reverse()
        with self.assertRaisesRegex(ValueError, 'indices differ'):
            audit.validate_landmarks(doc, {'test': part})


if __name__ == '__main__':
    unittest.main()
