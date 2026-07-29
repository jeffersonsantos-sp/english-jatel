# SKILL: add-language

Standardized pattern for adding a new language (es, fr, pt, etc.) to JATEL-IA.

## When to use
When adding a new language besides English (en), Spanish (es), and French (fr).

## Prerequisites
- Backup must be created first (use backup-procedures skill)
- All files listed below must be created/updated together

## Files to create/update

### 1. Grammar file
Create `backend/grammar_{lang}.json` with the same structure as `grammar.json`:
```json
{
  "levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
  "grammar": {
    "<nivel>": [
      {
        "topic": "...",
        "structure": "...",
        "explanation": "...",
        "examples": [
          "English sentence. — Translation.",
          "Another example."
        ]
      }
    ]
  }
}
```
- Copy A1 from grammar.json, then add A2–C2 with translated content.
- A1 is shared across all languages (same content as grammar.json A1).

### 2. MemHack file
Create `backend/memhack_{lang}.json` with the same structure as `memhack.json`:
```json
{
  "categories": ["category1", "category2", ...],
  "labels": {"category1": "Label in target lang", ...},
  "phrases": {
    "category1": [
      {"id": "cat1-1", "lang": "target lang phrase", "pt": "Portuguese translation"}
    ]
  }
}
```
- Categories must match phrase keys exactly.
- All categories must have the same number of phrases.
- The `lang` key in each phrase must match the file suffix (es→es, fr→fr, etc.).

### 3. Register lang in engine.py
- `LANG_VOICES` already has all 3 languages mapped; if adding a 4th, add its voice.
- `DEFAULT_LANG` stays "en".
- The `_memhack_file_for_lang` and `_grammar_file_for_lang` functions handle any lang suffix automatically.

### 4. Register lang in frontend
- `app.js` lang selector already handles any lang value (maps via `langMap` in `browserSpeak`).
- Add the option to the `<select id="lang">` in `frontend/index.html` if needed.
- `state.lang` is used dynamically for memhack phrases (`phrase[lang]`).

### 5. Update README.md, SKILL.md, prompts
- Update "idiomas suportados" if a new language is added.
- Update `.env.example` if new env vars are needed.
- Update this SKILL.md and the english-jatel SKILL.md.

### 6. Reload grammar
After adding grammar_{lang}.json, call `POST /api/admin/reload-grammar` with `lang={lang}` (admin only).

## Validation checklist
- [ ] grammar_{lang}.json has all 6 CEFR levels (A1–C2)
- [ ] memhack_{lang}.json categories and phrase keys match exactly
- [ ] All categories have the same number of phrases
- [ ] phrase keys match the lang suffix (e.g., "fr" for French)
- [ ] Frontend lang selector includes the new lang
- [ ] Backend loads the file without errors (check server logs)

## Example: adding Portuguese (pt)
1. Create `backend/grammar_pt.json` (copy EN, translate grammar topics)
2. Create `backend/memhack_pt.json` (translate all phrases to Portuguese pt)
3. No engine.py changes needed (file-based loading is automatic)
4. Add pt option to frontend lang selector
5. `POST /api/admin/reload-grammar` with `lang=pt`