# Translate Manga Codex Plugin

This repository is a repo-local Codex plugin marketplace for the `translate-manga` skill.

## Install

Clone this repository, then add the repository root as a Codex plugin marketplace:

```bash
codex plugin marketplace add /path/to/translate-manga
codex plugin add translate-manga@translate-manga
```

Start a new Codex thread after installation so the skill is loaded.

## Contents

- `.agents/plugins/marketplace.json`: Marketplace entry for Codex.
- `plugins/translate-manga/.codex-plugin/plugin.json`: Plugin manifest.
- `plugins/translate-manga/skills/translate-manga/SKILL.md`: Skill workflow instructions.
- `plugins/translate-manga/skills/translate-manga/scripts/validate_outputs.py`: Output validation helper.

## What The Skill Does

The skill defines a manga translation workflow for `image_gen.imagegen`:

- Use one fresh subagent for each generated manga page.
- Pass the source page as a `local_image`, not only as a filesystem path in text.
- Preserve panels, characters, black-and-white line art, halftones, and page structure.
- Replace visible original text with natural Simplified Chinese.
- Save outputs as deterministic files such as `002.zh.png`.
- Validate generated files with `skills/translate-manga/scripts/validate_outputs.py`.

## Local Validation

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/translate-manga
python3 /path/to/skill-creator/scripts/quick_validate.py plugins/translate-manga/skills/translate-manga
```
