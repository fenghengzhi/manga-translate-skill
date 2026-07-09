---
name: translate-manga
description: Workflow for translating local manga/comic page images into Simplified Chinese with image_gen.imagegen while preserving the original page art. Use when the user asks to 汉化/翻译 manga pages, regenerate numbered JPG/PNG pages, save translated outputs such as *.zh.png, process a multi-page chapter, use subagents for image generation, or avoid image_gen context contamination across pages.
---

# Translate Manga

## Core Rule

Use one isolated subagent for every `image_gen.imagegen` call.

`image_gen.imagegen` is context-sensitive. Do not run several manga pages through the same conversation context, and do not rely on a filesystem path written only in the prompt. Each page must be passed as a `local_image` item to a fresh subagent, and the subagent prompt must explicitly say to use the attached image as the base/reference image.

## Workflow

1. Identify the source pages and target names.
   - Preserve source images such as `002.jpg`; never edit them in place.
   - Use deterministic translated names such as `002.zh.png`.
   - If overwriting an existing translated output, overwrite only that target file.

2. Spawn one worker subagent per page.
   - Use `fork_context: false`.
   - Give each subagent exactly one `local_image`: its source page.
   - Give each subagent exactly one output path.
   - Do not pass previous generated outputs, neighboring pages, or multiple page images unless the user explicitly asks for cross-page style comparison.
   - For large chapters, run manageable batches and close completed agents promptly.

3. Instruct each subagent to call `image_gen.imagegen` exactly once.
   - Tell it that the attached `local_image` is the visual/base reference.
   - Tell it to preserve the same page: panels, characters, composition, black-and-white line art, halftones, aspect ratio, and non-text details.
   - Tell it to replace only visible text in speech bubbles, narration boxes, captions, signs, and SFX with natural Simplified Chinese.
   - Tell it not to invent a new page, add color, add watermarks, add signatures, add panels, or change the story.

4. Save the generated image into the project directory.
   - `image_gen` normally leaves PNGs under the active Codex generated-images directory, commonly `~/.codex/generated_images/<thread-or-agent-id>/`.
   - Copy the generated PNG to the requested target path; leave the generated original in place.
   - If dimensions differ from the source but the aspect ratio matches, resample only the translated output to the source dimensions when the chapter requires consistent page sizes. Do not modify the source image.
   - If dimensions or content do not match the source page, treat the page as failed and regenerate with a fresh subagent.

5. Verify before final response.
   - Check every target exists, is non-empty, and is a PNG.
   - Compare source and output dimensions.
   - Use `view_image` on source/output pairs for suspicious pages or any page the user challenges.
   - Confirm visually that the translated page still matches the original page structure and characters.

## Subagent Prompt Template

Use this shape for each page, filling in page id and paths:

```text
Task: Translate page NNN into Simplified Chinese by calling image_gen.imagegen exactly once, using the attached local_image as the visual/base reference. You are responsible only for page NNN.

Source image: /absolute/path/NNN.jpg
Output target: /absolute/path/NNN.zh.png

Important:
- The attached local_image is the source/reference image. In your image_gen prompt, explicitly instruct it to use the provided image as the base/reference image. Do not rely only on the filesystem path text.
- Preserve the same manga page: same characters, panels, composition, black-and-white art, linework, halftones, and aspect ratio.
- Replace only visible original text in speech bubbles/captions/narration/signs/SFX with natural Simplified Chinese.
- Do not invent a new page, add color, watermark, signature, extra panels, or new story content.
- After image_gen creates PNG, copy/save it to the exact output target above. Do not modify the source image.
- You are not alone in this filesystem. Do not delete, revert, or overwrite anything except your own output target.
- Final report whether image_gen was available, that the attached local_image was used as reference in the image_gen prompt, generated-from path, output path, dimensions if available, and whether output exists.
```

## Verification Script

Use `scripts/validate_outputs.py` for deterministic file checks after generation:

```bash
python3 /path/to/translate-manga/scripts/validate_outputs.py \
  "/path/to/chapter" --pages 1-22 --source-ext .jpg --target-suffix .zh.png
```

When the skill is installed from a plugin, locate this `SKILL.md` and use the sibling `scripts/validate_outputs.py` file in the same skill directory. The script checks source/target existence, PNG/JPEG dimensions, empty files, and count. It does not judge translation quality; always do visual checks when quality or page identity matters.
