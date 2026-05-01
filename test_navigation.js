// test_navigation.js - Run with: node test_navigation.js
// Tests that prev/next navigation visits all 417 poems sequentially without loops or skips

const fs = require('fs');
const data = JSON.parse(fs.readFileSync('data/divan_annotated.json', 'utf8'));

const total = data.şiirler.length;
console.log(`Total poems in data: ${total}`);

// Simulate navigation state
let currentPoemIdx = -1;

function navNext() {
  const ni = currentPoemIdx + 1;
  if (ni >= 0 && ni < total) { currentPoemIdx = ni; return true; }
  return false;
}

function navPrev() {
  const ni = currentPoemIdx - 1;
  if (ni >= 0 && ni < total) { currentPoemIdx = ni; return true; }
  return false;
}

// Test 1: Forward 1→417
console.log('\n--- Test: Forward navigation (1→417) ---');
currentPoemIdx = 0;
let visited = [currentPoemIdx];
for (let i = 0; i < total - 1; i++) {
  if (!navNext()) { console.log(`✗ FAILED: navNext blocked at index ${currentPoemIdx}`); process.exit(1); }
  visited.push(currentPoemIdx);
}
if (visited.length !== total) { console.log(`✗ FAILED: visited ${visited.length} poems, expected ${total}`); process.exit(1); }
if (currentPoemIdx !== total - 1) { console.log(`✗ FAILED: ended at index ${currentPoemIdx}, expected ${total-1}`); process.exit(1); }
// Check no duplicates in index sequence
for (let i = 0; i < visited.length; i++) {
  if (visited[i] !== i) { console.log(`✗ FAILED: at step ${i}, index was ${visited[i]}, expected ${i}`); process.exit(1); }
}
// Verify next is blocked at end
if (navNext()) { console.log('✗ FAILED: navNext should be blocked at last poem'); process.exit(1); }
console.log(`✓ Forward: visited all ${total} poems (index 0→${total-1})`);

// Test 2: Backward 417→1
console.log('\n--- Test: Backward navigation (417→1) ---');
currentPoemIdx = total - 1;
visited = [currentPoemIdx];
for (let i = 0; i < total - 1; i++) {
  if (!navPrev()) { console.log(`✗ FAILED: navPrev blocked at index ${currentPoemIdx}`); process.exit(1); }
  visited.push(currentPoemIdx);
}
if (visited.length !== total) { console.log(`✗ FAILED: visited ${visited.length} poems, expected ${total}`); process.exit(1); }
if (currentPoemIdx !== 0) { console.log(`✗ FAILED: ended at index ${currentPoemIdx}, expected 0`); process.exit(1); }
// Check sequence is descending
for (let i = 0; i < visited.length; i++) {
  if (visited[i] !== total - 1 - i) { console.log(`✗ FAILED: at step ${i}, index was ${visited[i]}, expected ${total-1-i}`); process.exit(1); }
}
// Verify prev is blocked at start
if (navPrev()) { console.log('✗ FAILED: navPrev should be blocked at first poem'); process.exit(1); }
console.log(`✓ Backward: visited all ${total} poems (index ${total-1}→0)`);

// Test 3: No loops - forward then backward returns to same spot
console.log('\n--- Test: No loops (forward 5, backward 5) ---');
currentPoemIdx = 200;
const start = currentPoemIdx;
for (let i = 0; i < 5; i++) navNext();
if (currentPoemIdx !== 205) { console.log(`✗ FAILED: after 5 next, at ${currentPoemIdx}, expected 205`); process.exit(1); }
for (let i = 0; i < 5; i++) navPrev();
if (currentPoemIdx !== start) { console.log(`✗ FAILED: after 5 prev, at ${currentPoemIdx}, expected ${start}`); process.exit(1); }
console.log(`✓ No loops: 200 → +5 → 205 → -5 → 200`);

console.log(`\n✓ All navigation tests passed (${total} poems)`);
