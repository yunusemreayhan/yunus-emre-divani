# Yûnus Emre Dîvânı

Interactive web reader for the complete Divan of Yunus Emre (13th century Anatolian Sufi poet), based on the critical edition by Yrd. Doç. Dr. Mustafa Tatcı.

**Live:** [yunusemreayhan.github.io/yunus-emre-divani](https://yunusemreayhan.github.io/yunus-emre-divani)

---

## Features

### Reading
- **417 poems**, 3496 beyits (couplets), fully searchable
- **Prev/Next navigation**, keyboard arrows, goto by number
- **2/4 line mode** — toggle mısra display density
- **Ottoman script toggle** — Latin ↔ Arabic script transliteration
- **TTS** — per-beyit 🔊 button + "Read All" (Web Speech API, Turkish male voice)
- **Responsive** — mobile-friendly single-page app

### Word Annotations
- **10,179 word-level annotations** with hover tooltips
- Old Turkish, Arabic, Persian vocabulary explained in modern Turkish
- Compound word support (sâz-kâr, bî-çâre, dem-be-dem, ene'l-hak, etc.)
- Suffix-aware matching: `pervânenün` → `pervâne`, `miskînlige` → `miskîn`
- Glossary from the book's SÖZLÜK section (1,881 entries) + 200+ manual additions

### Search
- **Fuzzy search**: `kal` finds `kâl`, `asik` finds `âşık`, `gonul` finds `gönül`
- Diacritics, soft consonants (ş/s, ç/c, ğ/g), and vowel variants (ı/i, ü/u, ö/o) all treated as equivalent
- Search matches poem text, özet (summary), and theme/concept tags

### Thematic Tags & Filtering
- Every poem tagged with: **temalar** (themes), **kavramlar** (Sufi concepts), **duygular** (emotions), **ahlak** (ethics)
- One-sentence Turkish **özet** (summary) for each poem
- **Tag filter chips** on home page — click to filter by theme/concept
- Colored badges on poem cards and headers

### Akaid (Creed) Notices
- **152 poems** (34%) flagged with Ehl-i Sünnet aqeedah concerns
- Pale amber notice box displayed before poems with potentially misleading mystical expressions
- Notices explain the **sekr** (spiritual intoxication) state and provide **tevil** (proper interpretation)
- Theological framework: İmam Rabbânî (Mektubat 2/44) and Said Nursî (26. Mektup)
- Key principles communicated:
  - "Ben Hak'ım" = "Ben yokum, yalnız Hak vardır" (not literal self-deification)
  - Vahdet-i vücud = like a person dazzled by sunlight who cannot see other lights
  - "Her şey O'dur" = "Her şey O'ndandır" (from Him, not IS Him)
  - Allah hulûl etmez, mahluk Allah olmaz, kul-Rab ayrımı daima bâkîdir

### Sharing & AI
- Per-beyit links to Google Translate, ChatGPT, Gemini for explanation
- Copy beyit with meanings, share poem via Twitter/Facebook/WhatsApp
- Disqus comments per poem

---

## Architecture

Single-page static app. No build step, no framework, no server. Hosted on GitHub Pages.

```
index.html              — entire frontend (HTML + CSS + JS)
data/
  divan.json            — 417 poems, structured (bölüm, vezin, beyitler)
  divan_annotated.json  — poems + per-beyit word meanings (anlamlar)
  poem_tags.json        — themes, concepts, özet, akaid notices
  sozluk.json           — glossary (word → meaning dictionary)
  skip_words.json       — common Turkish words excluded from annotation
```

### Data Pipeline

```
divan_raw.txt ──→ parse_divan.py ──→ data/divan.json
                  parse_glossary.py → data/sozluk.json

data/divan.json + data/sozluk.json ──→ annotate.py ──→ data/divan_annotated.json
```

The frontend fetches `divan_annotated.json` and `poem_tags.json` at runtime.

---

## Setup

```bash
git clone git@github.com:yunusemreayhan/yunus-emre-divani.git
cd yunus-emre-divani
make setup    # installs pre-commit hook (runs tests before every commit)
```

### Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install pre-commit hook (one-time) |
| `make test` | Run all unit tests |
| `make annotate` | Regenerate `divan_annotated.json` from sources |
| `make push` | Run tests + push to origin |
| `make clean` | Remove temp/batch files |

### Requirements

- **Node.js** (for tests)
- **Python 3** (for annotation pipeline)
- No npm packages, no pip packages — zero dependencies

---

## Annotation System

### How word matching works

`annotate.py` processes each beyit:

1. **Exact match** in glossary (`sozluk.json`) or `EXTRA_MEANINGS` dict
2. **Apostrophe-preserved lookup** (for `ma'nî`, `su'âl`, etc.)
3. **Diacritics-stripped lookup** (`â→a`, `î→i`, `û→u`)
4. **Verb root + mak/mek** lookup
5. **Suffix stripping** — tries removing Turkish suffixes (40+ patterns including `-lige`, `-lerün`, `-nün`, `-lere`, etc.) and checks if root is known
6. **Compound words** — hyphenated terms matched via `COMPOUND_MEANINGS` dict

### What gets skipped (no tooltip)

- Common modern Turkish words (915 in `skip_words.json`)
- Common verb conjugations (pattern-based: root ∈ common_roots + recognized suffix)
- Words ≤ 2 characters
- Proper nouns with suffixes (`Yûnus'un`, `Hakk'a`)

### Adding new words

Edit `EXTRA_MEANINGS` dict in `annotate.py`, then:

```bash
make annotate   # regenerates divan_annotated.json
make test       # verify nothing broke
```

---

## Tagging System

`data/poem_tags.json` — array of 417 objects:

```json
{
  "numara": 5,
  "ozet": "İlahi aşk iddiasında bulunan kişinin...",
  "temalar": ["aşk-ı ilahi", "zühd", "marifet"],
  "kavramlar": ["seyr-i süluk"],
  "duygular": ["aşk", "vecd"],
  "ahlak": ["tevazu", "hizmet"],
  "akaid_uyari": "short flag text...",
  "akaid_notu": "2-4 sentence notice with İmam Rabbani/Said Nursi tevil..."
}
```

### Tag Taxonomy

| Category | Values |
|----------|--------|
| **Temalar** | aşk-ı ilahi, zühd, takva, tevhid, marifet, nasihat, şikayet, münacaat, nefs, ölüm, fanilik, cennet, cehennem, sabır, şükür, tevbe |
| **Kavramlar** | vahdet-i vücud, fenâ-fillah, seyr-i süluk, şeriat-tarikat-hakikat, tecelli, müşahede, istiğna, cezbe, sekr, ilahi sarhoşluk |
| **Duygular** | korku-ahiret, korku-kabir, korku-hesap, korku-genel, aşk, hasret, vecd, hüzün, şükür, pişmanlık, ümit |
| **Ahlak** | tevazu, kibir-eleştirisi, hizmet, sabır, kanaat, cömertlik, riya-eleştirisi, dünya-eleştirisi |

### Theme Distribution

| Theme | Count | % |
|-------|-------|---|
| Aşk-ı ilahi | 265 | 64% |
| Marifet | 219 | 53% |
| Nasihat | 168 | 40% |
| Tevhid | 152 | 36% |
| Fanilik | 101 | 24% |
| Nefs | 78 | 19% |
| Zühd | 68 | 16% |
| Ölüm | 65 | 16% |

---

## Tests

```bash
node test_annotations.js    # 29 tests
```

Tests verify:
- Compound/archaic words have hover meanings (kîl, sâz-kâr, dünyâ-âhiret, hâzır, teslîm, pervânenün, âsil-zâdeler)
- Fuzzy search normalization (â→a, î→i, û→u, ı→i, ü→u, ö→o, ş→s, ç→c, ğ→g, apostrophe/hyphen stripped)
- Low-frequency words annotated (kâtil, sal, ma'nîsi, sinegile, bî-çâre)
- Common words NOT wrongly annotated (eyleye, gönülde)

Pre-commit hook runs all tests automatically — commit is blocked if any test fails.

---

## Source

Based on: **Yûnus Emre Dîvânı** — Hazırlayan: Yrd. Doç. Dr. Mustafa Tatcı (critical edition)

---

## License

Educational/personal project. Poem text is from a published critical edition. Code is MIT.
