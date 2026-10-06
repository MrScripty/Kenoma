/* Reflow only overflowing display MathML at top-level additive or equation
 * boundaries. Every token (including operators and spacing) is cloned in order;
 * nested fractions, powers and parenthesized expressions remain indivisible.
 * The original MathML and TeX annotation remain unchanged for the screen book. */
() => {
  const ns = 'http://www.w3.org/1998/Math/MathML';
  const rows = [];
  for (const equation of document.querySelectorAll('.equation')) {
    const original = equation.querySelector(':scope > math');
    const width = equation.clientWidth;
    if (!original) continue;
    const source = original.querySelector(':scope > semantics > mrow');
    if (source && source.getBoundingClientRect().width <= width + 0.5) continue;
    if (!source) throw new Error('Cannot reflow overflowing display equation');
    const tokens = [...source.children];
    const breaks = tokens.map((node, i) => i > 0 &&
      (node.localName === 'mspace' || (node.localName === 'mo' && ['+', '−', '='].includes(node.textContent))));
    const alternate = document.createElement('div');
    alternate.className = 'print-equation-rows';
    equation.append(alternate);
    equation.classList.add('print-reflowed');
    let start = 0;
    while (start < tokens.length) {
      const math = document.createElementNS(ns, 'math');
      math.setAttribute('display', 'block');
      const row = document.createElementNS(ns, 'mrow');
      math.append(row); alternate.append(math);
      let end = start, lastBreak = -1;
      while (end < tokens.length) {
        if (breaks[end] && end > start) lastBreak = end;
        row.append(tokens[end].cloneNode(true));
        end++;
        if (row.getBoundingClientRect().width > width + 0.5) {
          if (lastBreak <= start) throw new Error('Indivisible print math exceeds page width');
          end = lastBreak;
          row.replaceChildren(...tokens.slice(start, end).map(node => node.cloneNode(true)));
          break;
        }
      }
      if (row.getBoundingClientRect().width > width + 0.5) throw new Error('Print math still overflows');
      start = end;
    }
    const copied = [...alternate.querySelectorAll(':scope > math > mrow')].flatMap(row => [...row.children]);
    if (copied.length !== tokens.length || copied.some((node, i) => node.outerHTML !== tokens[i].outerHTML))
      throw new Error('Print math token sequence changed');
    rows.push({tex: original.querySelector('annotation')?.textContent, rows: alternate.children.length,
      tokenCount: tokens.length, maximumRowWidthPx: Math.max(...[...alternate.children].map(math => math.firstElementChild.getBoundingClientRect().width))});
  }
  const overflow = document.documentElement.scrollWidth > document.documentElement.clientWidth + 1;
  if (overflow) throw new Error('Print document has horizontal overflow');
  return {reflowed: rows, viewportWidthPx: document.documentElement.clientWidth, documentWidthPx: document.documentElement.scrollWidth};
}
