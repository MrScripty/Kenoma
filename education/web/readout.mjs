/** Deliberate spoken summary; callers invoke this only on the summary action. */
export function formatReadout(readout){
  return [...readout.children].map(row=>{
    const label=row.querySelector('dt').textContent.trim();
    const value=row.querySelector('dd').textContent.trim();
    return `${label}: ${value}.`;
  }).join(' ');
}
