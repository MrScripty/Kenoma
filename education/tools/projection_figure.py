"""Static fixed-vector reference; no constitutive law or equilibrium solve."""
from pathlib import Path


def generate(directory):
    g = [-.75, .25, -.25, .75]
    pg = [.125] * 4
    residual = [x - y for x, y in zip(g, pg)]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="640" height="310" viewBox="0 0 640 310" role="img"><title>Fixed sample field, weighted projection and residual</title><rect width="640" height="310" fill="white"/>']
    for col, (label, values, color) in enumerate([('g', g, '#385e68'), ('Pg', pg, '#087567'), ('g minus Pg', residual, '#bd663b')]):
        origin = 20 + col * 210
        parts.append(f'<text x="{origin}" y="28" font-size="18">{label}</text>')
        for value in [-1, 0, 1]:
            y = 160 - value * 85
            parts.append(f'<path d="M{origin+27} {y}h155" stroke="#bdc9cb"/><text x="{origin}" y="{y+5}" font-size="16">{value}</text>')
        for i, value in enumerate(values):
            x = origin + 45 + i * 39
            y = 160 - value * 85
            parts.append(f'<path d="M{x} 160V{y}" stroke="{color}" stroke-width="6"/><circle cx="{x}" cy="{y}" r="4" fill="{color}"/><text x="{x-5}" y="270" font-size="16">{i+1}</text>')
    parts.append('<text x="20" y="301" font-size="16">Same signed scale; Q1; w=(1,3,2,2); normalized samples.</text></svg>')
    (Path(directory) / 'pressure-projection.svg').write_text(''.join(parts))
