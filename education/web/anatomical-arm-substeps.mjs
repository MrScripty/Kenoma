/** Bounded transaction for the actual anatomical arm stepper.
 * Source/unit-tested candidate; no numerical recovery or anatomical acceptance
 * follows. No material law, contact rule, residual threshold or solver lives here.
 */
export const MAX_SUBDIVISION_DEPTH = 4;
export function advanceArmInterval(state, {
  h, maxDepth = 0, attempt, capture, restore,
}) {
  if (!Number.isFinite(h) || !(h > 0) || !Number.isInteger(maxDepth)
      || maxDepth < 0 || maxDepth > MAX_SUBDIVISION_DEPTH
      || typeof attempt !== 'function' || typeof capture !== 'function'
      || typeof restore !== 'function') throw new RangeError('Arm interval/subdivision contract');
  const initialRule = capture(), attempts = [], accepted = [];
  const limit = 2 ** (maxDepth + 1) - 1;
  function visit(current, dt, depth) {
    const rule = capture(), mark = accepted.length;
    let result;
    try {
      if (attempts.length >= limit) throw new RangeError('Arm attempt budget exhausted');
      // A failed callback cannot corrupt the caller's coordinates or work ledger.
      result = attempt(structuredClone(current), dt);
      if (!result || typeof result.accepted !== 'boolean' || !result.state)
        throw new TypeError('Arm attempt must return a state and explicit acceptance');
    } catch (error) {
      attempts.push({depth, hS: dt, accepted: false, exception: String(error)});
      restore(rule);
      return {accepted: false, state: current, reason: 'Arm attempt threw; interval rolled back',
              error: String(error), retryable: false};
    }
    attempts.push({depth, hS: dt, accepted: result.accepted, reason: result.reason ?? null});
    if (result.accepted) {
      accepted.push({hS: dt, receipt: result.receipt});
      return result;
    }
    restore(rule);
    if (depth === maxDepth) return {...result, state: current};
    const half = dt / 2;
    if (!(half > 0)) return {...result, state: current, reason: 'Arm substep underflow'};
    const first = visit(current, half, depth + 1);
    if (!first.accepted) {
      restore(rule); accepted.length = mark;
      return {...first, state: current};
    }
    const second = visit(first.state, half, depth + 1);
    if (!second.accepted) {
      restore(rule); accepted.length = mark;
      return {...second, state: current};
    }
    return second;
  }
  let result;
  try { result = visit(state, h, 0); }
  catch (error) {
    // Includes failures in rule capture or recursion infrastructure.
    restore(initialRule);
    throw error;
  }
  if (!result.accepted) { restore(initialRule); accepted.length = 0; }
  return {...result, state: result.accepted ? result.state : state,
    substepIntegration: {
      scope: 'SOURCE_UNIT_TESTED_NOT_NUMERICALLY_VALIDATED',
      requestedDurationS: h, maxDepth, attemptLimit: limit,
      attempts, committedSubsteps: accepted.length,
      receipts: accepted.map(row => ({hS: row.hS, receipt: row.receipt})),
      maximumAcceptedSubsteps: 2 ** maxDepth,
      anatomicalQualification: false,
    }};
}
