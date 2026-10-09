import init, { evaluate } from './pkg/human_wasm.js';

const failure = (code, message) => ({version: 1, ok: false, error: {code, message}});
const MAX_BYTES = 2 * 1024 * 1024;
// A plain JSON value boundary prevents NaN -> null, custom toJSON coercions,
// cycles and undefined before serialization. Rust validates u32 IDs/counts.
function validateValue(root) {
  const stack = [root], seen = new WeakSet();
  let count = 0;
  while (stack.length) {
    if (++count > MAX_BYTES) throw new Error('Input has too many values');
    const value = stack.pop();
    if (value === null || typeof value === 'string' || typeof value === 'boolean') continue;
    if (typeof value === 'number') {
      if (!Number.isFinite(value)) throw new Error('Numbers must be finite');
      continue;
    }
    if (typeof value !== 'object') throw new Error('Only plain JSON values are accepted');
    if (seen.has(value)) throw new Error('Cycles or repeated object references are not accepted');
    seen.add(value);
    if (!Array.isArray(value) && Object.getPrototypeOf(value) !== Object.prototype && Object.getPrototypeOf(value) !== null) {
      throw new Error('Only plain objects and arrays are accepted');
    }
    const descriptors = Object.getOwnPropertyDescriptors(value);
    for (const [key, descriptor] of Object.entries(descriptors)) {
      if (Array.isArray(value) && key === 'length') continue;
      if (!('value' in descriptor)) throw new Error('Accessors are not accepted');
      stack.push(descriptor.value);
    }
  }
}
/** Initialize once per JS realm. wasmUrl defaults relative to the generated module. */
export async function createSimpleGraph({wasmUrl} = {}) {
  await init(wasmUrl ? {module_or_path: wasmUrl} : undefined);
  return Object.freeze({
    /** Versioned request/response. Rig handles are local to this WASM instance; graph errors never return partial edits. */
    request(value) {
      let encoded;
      try {
        validateValue(value);
        encoded = JSON.stringify(value);
      } catch (error) {
        return failure('invalid_request', String(error.message));
      }
      if (new TextEncoder().encode(encoded).length > MAX_BYTES) return failure('resource_limit', 'Request exceeds 2 MiB');
      return JSON.parse(evaluate(encoded));
    },
  });
}
