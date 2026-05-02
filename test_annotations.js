#!/usr/bin/env node
/**
 * Unit tests for annotation and fuzzy search fixes.
 * Tests:
 * 1. Compound/archaic words get hover meanings (kîl, sâz-kâr, etc.)
 * 2. Fuzzy search normalization works correctly
 * 3. Low-frequency words are annotated (not just high-freq ones)
 */
const fs = require('fs');
const assert = require('assert');

const data = JSON.parse(fs.readFileSync('data/divan_annotated.json', 'utf8'));

let passed = 0, failed = 0;
function test(name, fn) {
  try { fn(); passed++; console.log(`  ✓ ${name}`); }
  catch(e) { failed++; console.log(`  ✗ ${name}: ${e.message}`); }
}

// Helper: get poem by number
function getPoem(num) { return data.şiirler.find(p => p.numara === num); }
// Helper: get anlamlar for a specific beyit
function getBeyitAnlamlar(poemNum, beyitNum) {
  const p = getPoem(poemNum);
  return p.beyitler.find(b => b.numara === beyitNum).anlamlar;
}

console.log('\n=== TEST 1: Compound/archaic words have hover meanings ===');

test('kîl has tooltip in poem 5 beyit 4', () => {
  const a = getBeyitAnlamlar(5, 4);
  assert(a['kîl'], 'kîl should have a meaning');
  assert(a['kîl'].includes('edikodu') || a['kîl'].includes('laf'), `kîl meaning should mention dedikodu/laf, got: ${a['kîl']}`);
});

test('kâl has tooltip in poem 5 beyit 4', () => {
  const a = getBeyitAnlamlar(5, 4);
  assert(a['kâl'], 'kâl should have a meaning');
});

test('sâz-kâr has tooltip in poem 2 beyit 6', () => {
  const a = getBeyitAnlamlar(2, 6);
  assert(a['sâz-kâr'], `sâz-kâr should have a meaning, keys: ${Object.keys(a)}`);
});

test('dünyâ-âhiret has tooltip in poem 2 beyit 2', () => {
  const a = getBeyitAnlamlar(2, 2);
  assert(a['dünyâ-âhiret'], `dünyâ-âhiret should have a meaning, keys: ${Object.keys(a)}`);
});

test('hâzır has tooltip in poem 5 beyit 4', () => {
  const a = getBeyitAnlamlar(5, 4);
  assert(a['hâzır'], `hâzır should have a meaning, keys: ${Object.keys(a)}`);
});

test('teslîm has tooltip in poem 5 beyit 4', () => {
  const a = getBeyitAnlamlar(5, 4);
  assert(a['teslîm'], `teslîm should have a meaning`);
});

test('pervânenün has tooltip in poem 5 beyit 5', () => {
  const a = getBeyitAnlamlar(5, 5);
  assert(a['pervânenün'], `pervânenün should have a meaning, keys: ${Object.keys(a)}`);
});

test('âsil-zâdeler has tooltip in poem 5 beyit 3', () => {
  const a = getBeyitAnlamlar(5, 3);
  assert(a['âsil-zâdeler'], `âsil-zâdeler should have a meaning, keys: ${Object.keys(a)}`);
});

console.log('\n=== TEST 2: Fuzzy search normalization ===');

// Extract fuzzyNorm from index.html
const html = fs.readFileSync('index.html', 'utf8');
const fnMatch = html.match(/function fuzzyNorm\(s\)\{[\s\S]*?\n\}/);
assert(fnMatch, 'fuzzyNorm function should exist in index.html');
eval(fnMatch[0]); // defines fuzzyNorm in this scope

test('â → a', () => assert.strictEqual(fuzzyNorm('kâl'), 'kal'));
test('î → i', () => assert.strictEqual(fuzzyNorm('kîl'), 'kil'));
test('û → u', () => assert.strictEqual(fuzzyNorm('nûr'), 'nur'));
test('ı → i', () => assert.strictEqual(fuzzyNorm('ışk'), 'isk'));
test('ü → u', () => assert.strictEqual(fuzzyNorm('gönül'), 'gonul'));
test('ö → o', () => assert.strictEqual(fuzzyNorm('ölüm'), 'olum'));
test('ş → s', () => assert.strictEqual(fuzzyNorm('âşık'), 'asik'));
test('ç → c', () => assert.strictEqual(fuzzyNorm('çâre'), 'care'));
test('ğ → g', () => assert.strictEqual(fuzzyNorm('dağ'), 'dag'));
test('apostrophe stripped', () => assert.strictEqual(fuzzyNorm("ma'nî"), 'mani'));
test('hyphen stripped', () => assert.strictEqual(fuzzyNorm('sâz-kâr'), 'sazkar'));

test('searching "kal" matches text containing "kâl"', () => {
  const text = 'sözde kîl ü kâl olmaya';
  assert(fuzzyNorm(text).includes(fuzzyNorm('kal')), 'kal should match kâl in text');
});

test('searching "asik" matches text containing "âşık"', () => {
  const text = 'âşık olan kişi';
  assert(fuzzyNorm(text).includes(fuzzyNorm('asik')), 'asik should match âşık');
});

test('searching "gonul" matches text containing "gönül"', () => {
  const text = 'gönül virürisen';
  assert(fuzzyNorm(text).includes(fuzzyNorm('gonul')), 'gonul should match gönül');
});

console.log('\n=== TEST 3: Low-frequency words are annotated ===');

test('kâtil (freq=4) annotated in poem 5 beyit 7', () => {
  const a = getBeyitAnlamlar(5, 7);
  assert(a['kâtil'], `kâtil should have a meaning, keys: ${Object.keys(a)}`);
});

test('sal (freq=4) annotated in poem 5 beyit 3', () => {
  const a = getBeyitAnlamlar(5, 3);
  assert(a['sal'], `sal should have a meaning, keys: ${Object.keys(a)}`);
});

test("ma'nîsi (freq=4) annotated in poem 5 beyit 3", () => {
  const a = getBeyitAnlamlar(5, 3);
  assert(a["ma'nîsi"], `ma'nîsi should have a meaning, keys: ${Object.keys(a)}`);
});

test('sinegile (freq=1) annotated in poem 5 beyit 5', () => {
  const a = getBeyitAnlamlar(5, 5);
  assert(a['sinegile'], `sinegile should have a meaning, keys: ${Object.keys(a)}`);
});

// Check that bî-çâre compound works across the corpus
test('bî-çâre compound annotated somewhere', () => {
  let found = false;
  for (const p of data.şiirler) {
    for (const b of p.beyitler) {
      if (b.anlamlar['bî-çâre']) { found = true; break; }
    }
    if (found) break;
  }
  assert(found, 'bî-çâre should be annotated in at least one beyit');
});

// Verify common words DON'T get wrong tooltips
console.log('\n=== TEST 4: Common words NOT wrongly annotated ===');

test('eyleye (common verb form) not annotated in poem 5 beyit 4', () => {
  const a = getBeyitAnlamlar(5, 4);
  assert(!a['eyleye'], `eyleye should NOT have a tooltip (it's a common verb form), but got: ${a['eyleye']}`);
});

test('gönülde not annotated in poem 5 beyit 4', () => {
  const a = getBeyitAnlamlar(5, 4);
  assert(!a['gönülde'], `gönülde should NOT have a tooltip (common), but got: ${a['gönülde']}`);
});

console.log(`\n${'='.repeat(50)}`);
console.log(`Results: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
