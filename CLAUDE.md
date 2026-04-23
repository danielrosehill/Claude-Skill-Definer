# Claude-Skill-Definer

This is a **workspace repo** for turning multimodal process captures (voice, video, images+text) into installable Claude Code skills.

## What you're doing here

When Daniel drops something into `inbox/`, your job is:

1. **Route** by modality to the right intake agent/command.
2. **Normalize** the capture into a process spec under `specs/<skill-name>.md` — a clean, ordered list of steps, inputs, outputs, edge cases.
3. **Author** a `SKILL.md` under `skills-staged/<skill-name>/` that conforms to the official skill format (YAML frontmatter with `name` + `description`, markdown body with triggers and instructions).
4. **Install** to the target (plugin path, repo `.claude/skills/`, or `~/.claude/skills/`) on request.

## Modality playbook

### Voice (`inbox/voice/*`)
- Transcribe with the `gemini-transcription` MCP (`transcribe_audio_raw` for fidelity, then `clean-transcript` skill to de-filler).
- Most voice notes are brain-dump style — expect out-of-order steps, tangents, and implicit context. Reconstruct the intended process, don't just transcribe.

### Video (`inbox/video/*`)
- Downsample first: `ffmpeg -i in.mp4 -vf "fps=1,scale=854:480" -c:v libx264 -crf 32 -c:a aac -b:a 64k out.mp4` (tune as needed — the goal is cheap enough to send to a vision model).
- Extract keyframes: `ffmpeg -i in.mp4 -vf "fps=1/5" frames/%04d.jpg` (1 frame per 5s).
- Extract audio: `ffmpeg -i in.mp4 -vn -acodec copy audio.m4a` then transcribe.
- Send frames + transcript jointly to a vision model (Gemini 2.x via `hf_jobs` or Claude w/ image input). Ask for a temporal process description.
- Video is the hardest modality — if a step is unclear, flag it in the spec rather than hallucinating.

### Images + text (`inbox/images/*` + `inbox/text/<same-basename>.md`)
- Read text first to understand intent, then examine images as anchors for UI state / visual context.
- If text and images disagree, text wins for intent, images win for specifics (button labels, field names).

### Text (`inbox/text/*`)
- Fastest path. Go straight to spec → SKILL.md.

## SKILL.md conventions

```markdown
---
name: skill-name-kebab-case
description: One sentence describing WHEN to use this skill. Start with "Use when…" or similar trigger phrasing so the harness picks it up.
---

# Skill body

Concrete instructions. Include file paths, commands, and decision points. Keep under ~150 lines unless the skill genuinely needs more.
```

Description quality matters most — it's what the harness matches against to decide whether to fire the skill.

## Install targets

Resolve from spec frontmatter `install_target:`:
- `plugin:<plugin-name>` → find plugin root, write to `<root>/skills/<name>/`
- `repo:<path>` → write to `<path>/.claude/skills/<name>/`
- `user` → write to `~/.claude/skills/<name>/`

After install, verify by listing the target dir and confirming the SKILL.md parses (frontmatter valid, name matches dir).

## What not to do

- Don't invent steps to fill gaps in ambiguous captures — flag them in the spec with `TODO:` or `?` and ask Daniel.
- Don't skip the `specs/` normalization step and jump straight to SKILL.md — the intermediate spec is where ambiguity gets resolved.
- Don't install to a target without confirming the path exists.
