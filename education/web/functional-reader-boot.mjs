/** Start elementary controls by default; archive solvers require explicit navigation. */
const profiles = [
  ['series', 'data-demo', 'series', 'lab-series'],
  ['material', 'data-material', 'compression', 'lab-property-material'],
  ['serial', 'data-serial', 'assembly', 'lab-serial-specimen'],
  ['spatial', 'data-advanced', 'spatial', 'lab-spatial'],
  ['continuum', 'data-advanced', 'continuum', 'lab-continuum'],
];
const requested = new URL(location.href).searchParams.get('laboratory');
const selected = profiles.some(([key]) => key === requested) ? requested : null;
for (const [key, attribute, value, id] of profiles) {
  const section = document.getElementById(id);
  if (!section || section.getAttribute(attribute) !== value) throw Error('Archive profile mismatch: ' + id);
  const notice = document.createElement('p');
  notice.className = 'archive-runtime-note';
  if (selected === key) {
    notice.textContent = 'Archived computational model enabled by your selection. Historical results and limits remain snapshot evidence; this release does not requalify this solver.';
  } else {
    section.removeAttribute(attribute);
    for (const control of section.querySelectorAll('input,select,button')) control.disabled = true;
    notice.append('Static archived example. This computational model starts only when selected. ');
    const link = document.createElement('a');
    const target = new URL(location.href);
    target.search = '';
    target.searchParams.set('laboratory', key);
    target.hash = id;
    link.href = target.pathname + target.search + target.hash;
    link.textContent = 'Open archived interactive model';
    notice.append(link);
  }
  section.prepend(notice);
}
document.documentElement.dataset.archiveProfile = selected || 'elementary';
await import('./app.js');
document.documentElement.dataset.elementaryControls = 'ready';
