# Translate Manga Codex Plugin

This repository packages the `translate-manga` Codex skill.

The skill defines a manga translation workflow for `image_gen.imagegen`:

- Use one fresh subagent for each generated manga page.
- Pass the source page as a `local_image`, not only as a filesystem path in text.
- Preserve panels, characters, black-and-white line art, halftones, and page structure.
- Replace visible original text with natural Simplified Chinese.
- Save outputs as deterministic files such as `002.zh.png`.
- Validate generated files with `skills/translate-manga/scripts/validate_outputs.py`.

## Contents

- `.codex-plugin/plugin.json`: Codex plugin manifest.
- `skills/translate-manga/SKILL.md`: Skill workflow instructions.
- `skills/translate-manga/scripts/validate_outputs.py`: Output file validation helper.

## Local Validation

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py .
python3 /path/to/skill-creator/scripts/quick_validate.py skills/translate-manga
```
