// test_split.js - Run with: node test_split.js

function countSyllables(t){return(t.toLowerCase().match(/[aeıioöuüâîû]/g)||[]).length}

function splitBeyit(text){
  const totalSyl=countSyllables(text);
  const target=Math.round(totalSyl/2);
  const words=text.split(/\s+/);
  let sylCount=0,bestIdx=Math.ceil(words.length/2),bestDiff=Infinity;
  for(let i=0;i<words.length;i++){
    sylCount+=countSyllables(words[i]);
    const diff=Math.abs(sylCount-target);
    if(diff<bestDiff){bestDiff=diff;bestIdx=i+1;}
  }
  return[words.slice(0,bestIdx).join(' '),words.slice(bestIdx).join(' ')];
}

// Test cases: [input, expected_line1, expected_line2]
const tests = [
  [
    "Gönlüm canum 'aklum bilüm senün ile karâr ider Pervâz ururlar dem-be-dem uçuban dosta gitmege",
    "Gönlüm canum 'aklum bilüm senün ile karâr ider",
    "Pervâz ururlar dem-be-dem uçuban dosta gitmege"
  ],
  [
    "İzzet ü erkân kamusı bunlardur dünyâ sevgüsi 'Işkdan haber eyitmesün kim dünyâ 'izzetin seve",
    "İzzet ü erkân kamusı bunlardur dünyâ sevgüsi",
    "'Işkdan haber eyitmesün kim dünyâ 'izzetin seve"
  ],
  [
    "Sensüz yola girürisem çârem yok adım atmaga Gevdemde kuvvetüm sensin başum götürüp gitmege",
    "Sensüz yola girürisem çârem yok adım atmaga",
    "Gevdemde kuvvetüm sensin başum götürüp gitmege"
  ],
  [
    "Ne elif okıdum ne cim ne varlıkdandur kelecim Bilmeye yüz bin müneccim tâli'üm ne ılduzdan gelür",
    "Ne elif okıdum ne cim ne varlıkdandur kelecim",
    "Bilmeye yüz bin müneccim tâli'üm ne ılduzdan gelür"
  ],
  [
    "'Işkun aldı benden beni Bana seni gerek seni Ben yanaram düni güni Bana seni gerek seni",
    "'Işkun aldı benden beni Bana seni gerek seni",
    "Ben yanaram düni güni Bana seni gerek seni"
  ],
  [
    "Keleci bilen kişinün yüzini ag ide bir söz Sözi bişürüp diyenün işini sag ide bir söz",
    "Keleci bilen kişinün yüzini ag ide bir söz",
    "Sözi bişürüp diyenün işini sag ide bir söz"
  ],
  [
    "Bize dîdâr gerek dünyâ gerekmez Bize ma'nî gerek da'vâ gerekmez",
    "Bize dîdâr gerek dünyâ gerekmez",
    "Bize ma'nî gerek da'vâ gerekmez"
  ],
];

let passed = 0, failed = 0;

tests.forEach(([input, exp1, exp2], i) => {
  const [got1, got2] = splitBeyit(input);
  const ok = got1 === exp1 && got2 === exp2;
  if (ok) {
    passed++;
    console.log(`✓ Test ${i+1}: ${countSyllables(got1)}/${countSyllables(got2)}`);
  } else {
    failed++;
    console.log(`✗ Test ${i+1} FAILED:`);
    console.log(`  Expected: "${exp1}" | "${exp2}"`);
    console.log(`  Got:      "${got1}" | "${got2}"`);
    console.log(`  Syllables: ${countSyllables(got1)}/${countSyllables(got2)}`);
  }
});

console.log(`\n${passed}/${passed+failed} tests passed`);
if (failed > 0) process.exit(1);
