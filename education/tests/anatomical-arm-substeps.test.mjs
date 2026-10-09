import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {advanceArmInterval,MAX_SUBDIVISION_DEPTH} from '../web/anatomical-arm-substeps.mjs';

// Metadata-only callbacks. Never import the arm/material/element/solver modules.
const initial = () => ({timeS: 0, qRad: .25, activation: .1, massKg: .5,
  coordinatesM: new Float64Array([1, 2]), history: [], mechanicalWorkJ: 0});
function fixture(callback) {
  let rule = {knots: ['original'], generation: 0};
  return {capture: () => structuredClone(rule), restore: r => {rule = structuredClone(r);},
    rule: () => structuredClone(rule), attempt: (s, h) => callback(s, h, rule)};
}
function success(s, h, rule) {
  const receipt = {hS: h, token: s.history.length + 1};
  rule.knots.push('accepted'); rule.generation++;
  return {accepted: true, state: {...s, timeS: s.timeS + h,
    history: [...s.history, receipt], mechanicalWorkJ: s.mechanicalWorkJ + h}, receipt};
}

test('depth zero performs one attempt and preserves the receipt', () => {
  const s = initial(), f = fixture(success);
  const r = advanceArmInterval(s, {...f, h: .125});
  assert.equal(r.accepted, true); assert.equal(r.state.timeS, .125);
  assert.deepEqual(r.receipt, {hS: .125, token: 1});
  assert.equal(r.substepIntegration.attempts.length, 1);
  assert.equal(r.substepIntegration.committedSubsteps, 1);
  assert.equal(s.timeS, 0); assert.deepEqual(s.history, []);
});

test('one rejected whole step then two accepted halves commits the interval', () => {
  const s = initial(), f = fixture((s, h, rule) => {
    if (h > .0625) {rule.knots.push('rejected'); return {accepted: false, state: s, reason: 'fixture refusal'};}
    return success(s, h, rule);
  });
  const r = advanceArmInterval(s, {...f, h: .125, maxDepth: 1});
  assert.equal(r.accepted, true); assert.equal(r.state.timeS, .125);
  assert.equal(r.state.mechanicalWorkJ, .125); assert.equal(r.state.massKg, .5);
  assert.deepEqual(r.substepIntegration.attempts.map(a => a.hS), [.125, .0625, .0625]);
  assert.deepEqual(r.state.history.map(row => row.hS), [.0625, .0625]);
  assert.deepEqual(f.rule().knots, ['original', 'accepted', 'accepted']);
});

test('late-half failure rolls back coordinates, time, activation, work, history and contact', () => {
  const s = initial(), before = structuredClone(s);
  const f = fixture((s, h, rule) => {
    s.coordinatesM[0] = 900; s.activation = .8;
    if (h > .0625 || s.timeS > 0) {rule.knots.push('failed'); return {accepted: false, state: s, reason: 'fixture refusal'};}
    return success(s, h, rule);
  });
  const r = advanceArmInterval(s, {...f, h: .125, maxDepth: 1});
  assert.equal(r.accepted, false); assert.equal(r.state, s); assert.deepEqual(s, before);
  assert.equal(r.substepIntegration.committedSubsteps, 0);
  assert.deepEqual(r.substepIntegration.receipts, []);
  assert.deepEqual(f.rule(), {knots: ['original'], generation: 0});
});

test('nested recovery retains only accepted leaf receipts', () => {
  const f = fixture((s, h, rule) => h > .03125
    ? {accepted: false, state: s, reason: 'fixture refusal'} : success(s, h, rule));
  const r = advanceArmInterval(initial(), {...f, h: .125, maxDepth: 2});
  assert.equal(r.accepted, true); assert.equal(r.substepIntegration.attempts.length, 7);
  assert.equal(r.substepIntegration.committedSubsteps, 4);
  assert.deepEqual(r.state.history.map(row => row.hS), [.03125, .03125, .03125, .03125]);
});

test('depth four enforces 31 attempted solves and 16 accepted leaves maximum', () => {
  const f = fixture((s, h, rule) => h > .0078125
    ? {accepted: false, state: s, reason: 'fixture refusal'} : success(s, h, rule));
  const r = advanceArmInterval(initial(), {...f, h: .125, maxDepth: 4});
  assert.equal(r.substepIntegration.attempts.length, 31);
  assert.equal(r.substepIntegration.attemptLimit, 31);
  assert.equal(r.substepIntegration.committedSubsteps, 16);
  assert.equal(r.state.timeS, .125);
});

test('all refusals stop at the leftmost bounded leaf and restore the initial state', () => {
  const s = initial(), f = fixture((s, h, rule) => {
    rule.generation++; return {accepted: false, state: s, reason: 'unchanged physical gate refused'};
  });
  const r = advanceArmInterval(s, {...f, h: .125, maxDepth: 4});
  assert.equal(r.accepted, false); assert.equal(r.state, s);
  assert.equal(r.substepIntegration.attempts.length, 5);
  assert.equal(r.reason, 'unchanged physical gate refused');
  assert.deepEqual(f.rule(), {knots: ['original'], generation: 0});
});

test('exceptions are terminal and do not authorize subdivision retries', () => {
  const s = initial(), f = fixture((s, h, rule) => {
    rule.knots.push('exception'); s.coordinatesM[1] = 999; throw new RangeError('fixture exception');
  });
  const r = advanceArmInterval(s, {...f, h: .125, maxDepth: 4});
  assert.equal(r.accepted, false); assert.equal(r.state, s);
  assert.equal(r.substepIntegration.attempts.length, 1);
  assert.equal(r.retryable, false); assert.deepEqual([...s.coordinatesM], [1, 2]);
  assert.deepEqual(f.rule(), {knots: ['original'], generation: 0});
});

test('late exception discards previously accepted provisional work', () => {
  const s = initial(), f = fixture((s, h, rule) => {
    if (h > .0625) return {accepted: false, state: s};
    if (s.timeS > 0) {rule.generation++; throw Error('late fixture exception');}
    return success(s, h, rule);
  });
  const r = advanceArmInterval(s, {...f, h: .125, maxDepth: 1});
  assert.equal(r.accepted, false); assert.equal(r.state, s);
  assert.equal(r.substepIntegration.committedSubsteps, 0);
  assert.deepEqual(f.rule(), {knots: ['original'], generation: 0});
});

test('bad depth/duration is rejected before any attempt or contact mutation', () => {
  const f = fixture(success);
  for (const [h, maxDepth] of [[Infinity, 1], [NaN, 0], [0, 0], [-1, 1], [.1, -1], [.1, 5], [.1, 1.5]]) {
    assert.throws(() => advanceArmInterval(initial(), {...f, h, maxDepth}), RangeError);
    assert.deepEqual(f.rule(), {knots: ['original'], generation: 0});
  }
});

test('invalid acceptance metadata refuses without retries', () => {
  const f = fixture(s => ({accepted: 'yes', state: s}));
  const r = advanceArmInterval(initial(), {...f, h: .125, maxDepth: 4});
  assert.equal(r.accepted, false); assert.equal(r.substepIntegration.attempts.length, 1);
});

test('new implementation does not inherit physical qualification', () => {
  const r = advanceArmInterval(initial(), {...fixture(success), h: .125});
  assert.equal(r.substepIntegration.scope, 'SOURCE_UNIT_TESTED_NOT_NUMERICALLY_VALIDATED');
  assert.equal(r.substepIntegration.anatomicalQualification, false);
});

test('actual arm integration preserves the complete old solve/law/gate source bytes', () => {
  let source = readFileSync(new URL('../web/anatomical-arm.mjs', import.meta.url), 'utf8');
  source = source.replace("import {advanceArmInterval,MAX_SUBDIVISION_DEPTH} from './anatomical-arm-substeps.mjs';\n", '');
  source = source.replace('function attemptAnatomicalArmStep(', 'export function stepAnatomicalArm(');
  const begin = source.indexOf('// Opt-in source candidate:');
  const end = source.indexOf('export function changeAnatomicalMass(', begin);
  assert.ok(begin >= 0 && end > begin); source = source.slice(0, begin) + source.slice(end);
  assert.equal(createHash('sha256').update(source).digest('hex'), '9ec37ec7b23bb67643fef715f4554fc8811e897a581691231e6669fdd66c7569');
});

test('worker opt-in and trace wiring preserve every previous worker statement', () => {
  let source = readFileSync(new URL('../web/anatomical-arm-worker.mjs', import.meta.url), 'utf8');
  source = source.replace(',...(data.subdivisionDepth==null?{}:{subdivisionDepth:data.subdivisionDepth})', '');
  source = source.replace(',...(result.substepIntegration?{substepIntegration:result.substepIntegration}:{})', '');
  assert.equal(createHash('sha256').update(source).digest('hex'), 'dfadf3136b8ecac0fd6275f059085636eb8953346d920ca69a4d4382fa7b39d5');
});

function publicWrapper(attempt) {
  // Compile just the actual public wrapper with injected metadata callbacks.
  // No imports or old physical solve body are evaluated.
  const source = readFileSync(new URL('../web/anatomical-arm.mjs', import.meta.url), 'utf8');
  const begin = source.indexOf('export function stepAnatomicalArm(');
  const end = source.indexOf('export function changeAnatomicalMass(', begin);
  const wrapper = source.slice(begin, end).replace('export function', 'function');
  return new Function('advanceArmInterval', 'MAX_SUBDIVISION_DEPTH', 'contactRecipe',
    'restoreContactRecipe', 'attemptAnatomicalArmStep', wrapper + '\nreturn stepAnatomicalArm;')(
      advanceArmInterval, MAX_SUBDIVISION_DEPTH, c => structuredClone(c.rule),
      (c, r) => {c.rule = structuredClone(r);}, attempt);
}

test('actual public wrapper forwards effort and timestep into original-step callback', () => {
  const calls = [], s = initial(), arm = {parameters: {stepS: .125}, contact: {rule: {knots: ['stale']}},
    initialContactRule: {knots: ['fallback']}};
  s.contactRule = {knots: ['state rule']};
  const step = publicWrapper((a, current, options) => {
    assert.equal(a, arm); calls.push(options);
    if (options.h > .0625) {a.contact.rule.knots.push('rejected'); return {accepted: false, state: current};}
    a.contact.rule.knots.push('accepted');
    return {accepted: true, state: {...current, timeS: current.timeS + options.h}, receipt: {hS: options.h}};
  });
  const r = step(arm, s, {effort: .3, subdivisionDepth: 1});
  assert.equal(r.accepted, true); assert.equal(r.state.timeS, .125);
  assert.deepEqual(calls.map(c => [c.effort, c.h, c.maxIterations]), [[.3, .125, 120], [.3, .0625, 120], [.3, .0625, 120]]);
  assert.deepEqual(arm.contact.rule.knots, ['state rule', 'accepted', 'accepted']);
  assert.deepEqual(s.contactRule.knots, ['state rule']);
});

test('actual public wrapper restores the state contact recipe after terminal refusal', () => {
  const s = initial(), arm = {parameters: {stepS: .125}, contact: {rule: {generation: 99}}, initialContactRule: {generation: 0}};
  s.contactRule = {generation: 3};
  const step = publicWrapper((a, current) => {a.contact.rule.generation = 900; throw Error('mock solver error');});
  const r = step(arm, s, {effort: .3, subdivisionDepth: 4});
  assert.equal(r.accepted, false); assert.equal(r.state, s);
  assert.deepEqual(arm.contact.rule, {generation: 3});
  assert.equal(r.substepIntegration.attempts.length, 1);
});

test('custom warm start remains available at depth zero; subdivision refuses it before mutation', () => {
  const s = initial(), guess = new Float64Array([5, 6]);
  const arm = {parameters: {stepS: .125}, contact: {rule: {generation: 0}}, initialContactRule: {generation: 0}};
  let calls = 0;
  const step = publicWrapper((a, current, options) => {
    calls++; assert.equal(options.startCoordinates, guess); return {accepted: false, state: current};
  });
  step(arm, s, {effort: .3, startCoordinates: guess}); assert.equal(calls, 1);
  const before = structuredClone(arm.contact);
  assert.throws(() => step(arm, s, {effort: .3, startCoordinates: guess, subdivisionDepth: 1}), RangeError);
  assert.equal(calls, 1); assert.deepEqual(arm.contact, before);
});

test('default bypass preserves exact state/options/result and every retained alias', () => {
  const s = initial(), options = {effort: '0.3', h: '.125'}, result = {accepted: true, state: s};
  s.massEvents = [{externalWorkJ: 4}]; s.history = [{nested: {value: 2}}];
  const arm = {}; // No parameter/contact access is needed before the original callback.
  const step = publicWrapper((a, current, forwarded) => {
    assert.equal(a, arm); assert.equal(current, s); assert.equal(forwarded, options);
    assert.equal(current.massEvents, s.massEvents); assert.equal(current.history[0], s.history[0]);
    return result;
  });
  assert.equal(step(arm, s, options), result);
  assert.equal(Object.hasOwn(result, 'substepIntegration'), false);
});

test('default bypass propagates original exceptions and performs no new domain checks', () => {
  const error = new RangeError('Effort/step domain'), options = {effort: Infinity, h: Infinity};
  const step = publicWrapper((a, s, forwarded) => {assert.equal(forwarded, options); throw error;});
  assert.throws(() => step({}, initial(), options), e => e === error);
});

test('late refusal preserves every state value and caller identity', () => {
  const s = {...initial(), omegaRadPerS: .2, effort: .3, step: 7,
    contactRule: {schema: 1, tendonKnots: [['0:0', [.1, .2]]]},
    massEvents: [{massKg: .5, externalEnergyJ: 2}], history: [{nested: [2, 3]}]};
  const before = structuredClone(s), history = s.history, massEvents = s.massEvents;
  const f = fixture((current, h, rule) => {
    const late = current.timeS > 0;
    current.coordinatesM.fill(999); current.qRad = 10; current.omegaRadPerS = 20;
    current.activation = .9; current.effort = .8; current.massKg = 99;
    current.step = 999; current.mechanicalWorkJ = 100;
    current.contactRule.tendonKnots[0][1].push(.4);
    current.massEvents[0].externalEnergyJ = 999; current.history[0].nested.push(999);
    rule.generation++; rule.knots.push('provisional');
    return h > .0625 || late ? {accepted: false, state: current} : success(current, h, rule);
  });
  const r = advanceArmInterval(s, {...f, h: .125, maxDepth: 1});
  assert.equal(r.accepted, false); assert.equal(r.state, s); assert.deepEqual(s, before);
  assert.equal(s.history, history); assert.equal(s.massEvents, massEvents);
  assert.deepEqual(f.rule(), {knots: ['original'], generation: 0});
});

function workerFixture(step, s = initial()) {
  // Execute the actual worker handler, injecting the original-step callback only.
  // No initialization, fetch, original numerical modules or sample evaluation.
  const source = readFileSync(new URL('../web/anatomical-arm-worker.mjs', import.meta.url), 'utf8')
    .split('\n').filter(line => !line.startsWith('import ')).join('\n')
    .replace('let arm,state,initial,epoch=0;', 'let arm=injectedArm,state=injectedState,initial,epoch=0;');
  const posts = [], self = {postMessage: p => posts.push(structuredClone(p))}, arm = {};
  new Function('self', 'injectedArm', 'injectedState', 'stepAnatomicalArm', source)(self, arm, s, step);
  return {posts, arm, send: data => self.onmessage({data: {id: 1, epoch: 0, kind: 'step', ...data}})};
}

test('actual default worker preserves original options and posted message shape', async () => {
  const w = workerFixture((a, s, options) => {
    assert.deepEqual(options, {effort: .3, maxIterations: 120});
    a.onIteration({iteration: 1, maxGradient: 2});
    return {accepted: false, state: s, reason: 'unchanged refusal'};
  });
  await w.send({effort: .3});
  assert.equal(w.posts.length, 2); assert.equal(w.posts[0].kind, 'progress');
  assert.equal(Object.hasOwn(w.posts[1], 'substepIntegration'), false);
  assert.equal(w.posts[1].accepted, false);
});

test('actual default worker retains its error branch and opt-in metadata remains explicit', async () => {
  const failing = workerFixture(() => {throw new RangeError('Effort/step domain');});
  await failing.send({effort: .3});
  assert.deepEqual(failing.posts, [{id: 1, epoch: 0, kind: 'step', error: 'RangeError: Effort/step domain'}]);
  const opted = workerFixture((a, s, options) => {
    assert.equal(options.subdivisionDepth, 1);
    return {accepted: false, state: s, substepIntegration: {committedSubsteps: 0}};
  });
  await opted.send({effort: .3, subdivisionDepth: 1});
  assert.deepEqual(opted.posts[0].substepIntegration, {committedSubsteps: 0});
});

test('actual contact recipe restores all mutable fields and rebuilds derived sample values', () => {
  // Read source only; compile the two actual serialization functions with
  // metadata rebuild callbacks. No contact module import or atlas sampling.
  const source = execFileSync('git', ['show', 'HEAD:education/web/anatomical-contact-refinement.mjs'],
    {cwd: new URL('../..', import.meta.url), encoding: 'utf8'});
  const functions = source.slice(source.indexOf('export function contactRecipe(')).replaceAll('export function', 'function');
  const surfaceRebuild = s => {s.samples = {derivedFrom: structuredClone(s.materialTriangles)};};
  const boneRebuild = b => {b.samples = {derivedFrom: structuredClone(b.materialTriangles)};};
  const {capture, restore} = new Function('rebuildSurfaceSamples', 'rebuildBoneSamples',
    functions + '\nreturn {capture:contactRecipe,restore:restoreContactRecipe};')(surfaceRebuild, boneRebuild);
  const contact = {surfaces: [{materialTriangles: [[['surface rule']]], body: {unchanged: true}}],
    bones: [{materialTriangles: [[['bone rule']]], source: {unchanged: true}, referenceSamples: ['base']},
      {referenceSamples: ['unrefined base']}], tendonKnots: new Map([['0:0', [.1, .3]]]), refinementRounds: 3};
  surfaceRebuild(contact.surfaces[0]); boneRebuild(contact.bones[0]);
  contact.bones[1].samples = contact.bones[1].referenceSamples;
  const before = structuredClone(contact), recipe = capture(contact), sourceAlias = contact.bones[0].source;
  contact.surfaces[0].materialTriangles[0][0].push('changed'); contact.surfaces[0].samples = ['changed'];
  contact.bones[0].materialTriangles[0][0].push('changed'); contact.bones[0].samples = ['changed'];
  contact.bones[1].materialTriangles = [['new partition']]; contact.bones[1].samples = ['new samples'];
  contact.tendonKnots.get('0:0').push(.9); contact.tendonKnots.set('new', [.5]); contact.refinementRounds++;
  restore(contact, recipe);
  assert.deepEqual(contact, before); assert.equal(contact.bones[0].source, sourceAlias);
  assert.equal(Object.hasOwn(contact.bones[1], 'materialTriangles'), false);
  assert.equal(contact.bones[1].samples, contact.bones[1].referenceSamples);
  assert.deepEqual(capture(contact), recipe);
});
