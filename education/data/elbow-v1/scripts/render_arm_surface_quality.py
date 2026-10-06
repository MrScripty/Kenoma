#!/usr/bin/env python3
"""Static visual evidence from unchanged original atlas triangles; no acquisition."""
import hashlib
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

import audit_arm_surface_quality as audit


def draw(ax, part, dims, color, alpha=1, faces=None):
    vertices = np.asarray(part['vertices_m'])
    indices = np.asarray(part['triangles_zero_based'] if faces is None else faces)
    polygons = vertices[indices][:, :, dims]
    ax.add_collection(PolyCollection(polygons, facecolors=color, edgecolors='#18202d',
                                     linewidths=.13, alpha=alpha))
    ax.autoscale_view()
    ax.set_aspect('equal')
    ax.set_xlabel('XYZ'[dims[0]] + ' (m)')
    ax.set_ylabel('XYZ'[dims[1]] + ' (m)')
    ax.grid(alpha=.15)


def main():
    contract = audit.inventory.load(audit.OUT / 'input-contract.json')
    for item in contract['pins']:
        audit.inventory.verify_pin(audit.REPO, item)
    quality = audit.inventory.load(audit.OUT / 'quality.json')
    inventory = audit.inventory.load(audit.inventory.CURATION / 'source-inventory.json')
    atlas = audit.inventory.load(audit.REPO / inventory['owners']['source_coordinates'])
    attachments = audit.inventory.load(audit.REPO / inventory['owners']['current_attachments'])
    colors = list(plt.get_cmap('tab10').colors)
    plt.rcParams.update({'font.size': 8, 'figure.facecolor': '#f7f8fb', 'axes.facecolor': '#f7f8fb'})
    fig, axs = plt.subplots(2, 5, figsize=(16, 9), layout='constrained')
    for ax, part, row, color in zip(axs.flat, atlas['parts'], quality['parts'], colors):
        draw(ax, part, [0, 2], color)
        components = row['exact_coordinate_topology_diagnostic']['face_connected_components']
        for component in components:
            indices = component['source_faces_if_small_component_zero_based']
            if indices:
                faces = [part['triangles_zero_based'][i] for i in indices]
                draw(ax, part, [0, 2], '#e0009a', faces=faces)
                points = np.asarray(part['vertices_m'])[np.asarray(faces)].reshape(-1, 3)
                ax.scatter(*points.mean(axis=0)[[0, 2]], s=60, facecolors='none', edgecolors='#e0009a', linewidths=1)
        ax.set_title(part['name'].replace(' of right', '\nof right') + '\n' + part['element_id'] +
                     f" | {len(components)} welded component(s)")
    fig.suptitle('Ten original reduced atlas surfaces | X–Z projection, individual scales\n'
                 'Magenta circles locate small detached components; circle size is illustrative. No repairs.', fontsize=13)
    fig.savefig(audit.OUT / 'individual-surfaces.png', dpi=140, metadata={'Software': 'Kenoma read-only atlas audit'})
    plt.close(fig)
    fig, axs = plt.subplots(1, 3, figsize=(15, 9), layout='constrained')
    for ax, dims, title in zip(axs, [[0, 2], [1, 2], [0, 2]],
                              ['Full atlas X–Z projection', 'Full atlas Y–Z projection', 'Elbow bone patches / authored picks']):
        for part, color in zip(atlas['parts'], colors):
            if ax is axs[2] and part['element_id'] not in {'FJ3368', 'FJ3349', 'FJ3391'}:
                continue
            draw(ax, part, dims, color, alpha=.5 if ax is not axs[2] else .8)
        ax.set_title(title)
    axs[2].set_xlim(-.255, -.185)
    axs[2].set_ylim(.990, 1.080)
    parts = {p['element_id']: p for p in atlas['parts']}
    for name, patch in attachments['patches'].items():
        part = parts[patch['element_id']]
        faces = [part['triangles_zero_based'][i] for i in patch['triangle_indices_zero_based']]
        draw(axs[2], part, [0, 2], '#d00050', .65, faces)
    for pick in quality['landmarks']:
        x, _, z = pick['position_m']
        if .990 <= z <= 1.080:
            axs[2].scatter(x, z, s=12, color='black', zorder=10)
            axs[2].annotate(pick['id'], (x, z), xytext=(4, 5), textcoords='offset points', fontsize=7, zorder=10)
    fig.suptitle('Unchanged atlas coordinates in metres | +X left, +Y posterior, +Z superior\n'
                 'Static reconstructed reference; exact acquisition pose unknown. Pink bone patches and black picks are authored candidates.', fontsize=12)
    fig.savefig(audit.OUT / 'atlas-and-landmarks.png', dpi=140, metadata={'Software': 'Kenoma read-only atlas audit'})
    plt.close(fig)
    receipt = {'schema_version': 1, 'source_inventory_sha256': audit.pin(audit.inventory.CURATION / 'source-inventory.json')['sha256'],
               'quality_sha256': audit.pin(audit.OUT / 'quality.json')['sha256'],
               'renderer_sha256': audit.pin(audit.REPO / 'education/data/elbow-v1/scripts/render_arm_surface_quality.py')['sha256'],
               'matplotlib_version': matplotlib.__version__, 'numpy_version': np.__version__,
               'projections': ['X-Z individual', 'X-Z full atlas', 'Y-Z full atlas', 'X-Z elbow bones and authored landmarks'],
               'source_geometry_modified': False,
               'limits': 'Orthographic triangle projections with transparency; occlusion and overlapping projections limit depth interpretation. No anatomy validation or calibrated joint pose.',
               'images': [audit.pin(audit.OUT / p) for p in ['individual-surfaces.png', 'atlas-and-landmarks.png']]}
    (audit.OUT / 'render-checkpoint.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'images': [p['path'] for p in receipt['images']]}))


if __name__ == '__main__':
    main()
