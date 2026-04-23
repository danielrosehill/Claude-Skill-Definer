# Claude-Skill-Definer

Workspace for streamlining the creation of Claude Code skills via multimodal process definition.

Drop a voice note, screen recording, screenshots, or a scribbled text spec into `inbox/`, and agents will extract the process, normalize it into a spec, author a `SKILL.md`, and install it to a target plugin, repo, or the user-level `~/.claude/skills/` path.

## Why a workspace (not a plugin)

Skill authoring is stateful and iterative — raw captures land in `inbox/`, get normalized in `specs/`, staged in `skills-staged/`, then installed. Workspaces are designed for that flow; plugins are for distributable stateless commands. A plugin could be extracted later once the intake pipeline stabilizes.

## Directory layout

```
inbox/
  voice/      # .wav .mp3 .m4a — transcribed via gemini-transcription MCP
  video/      # .mp4 .mkv .webm — downsampled, frames + audio extracted, process inferred
  images/     # .png .jpg — screenshots, whiteboards, diagrams (paired with text)
  text/       # .md .txt — written process descriptions (possibly paired with images)
specs/        # normalized process definitions (one markdown file per skill)
skills-staged/ # generated SKILL.md + supporting scripts, pre-install
scripts/      # helpers (ffmpeg downsample, frame extract, install-to-target)
docs/         # notes on skill authoring conventions
.claude/
  agents/     # subagents: transcription-router, video-extractor, image-text-fusor, skill-author, skill-installer
  commands/   # slash commands: /define-from-voice, /define-from-video, /define-from-images, /define-from-text, /install-skill
```

## Input modalities

### Voice note
Place `.wav`/`.mp3`/`.m4a` in `inbox/voice/`. Transcription via the `gemini-transcription` MCP (raw preset). Transcript is cleaned of filler, then the `skill-author` agent extracts the implied process.

### Video
Place `.mp4`/`.mkv`/`.webm` in `inbox/video/`. Pipeline:
1. `ffmpeg` downsamples to a small resolution (e.g. 480p, 1 fps keyframes).
2. Audio track is extracted and transcribed.
3. Sampled frames are sent to a vision-capable model (Gemini 2.x or Claude with image input) together with the transcript.
4. The agent produces a step-by-step process narrative.

### Images + text
Place screenshots/diagrams in `inbox/images/` and a matching text file (same basename) in `inbox/text/`. The `image-text-fusor` agent considers them jointly — text provides intent, images anchor UI state.

### Text only
Plain markdown or txt in `inbox/text/`. Fastest path — straight to `skill-author`.

## Install targets

The `skill-installer` agent resolves one of:
- **Plugin** — `<plugin-root>/skills/<skill-name>/SKILL.md` (looked up via cached marketplace indexes)
- **Repo** — `<repo>/.claude/skills/<skill-name>/SKILL.md`
- **User-level** — `~/.claude/skills/<skill-name>/SKILL.md`

Target is specified in the spec frontmatter (`install_target:`) or chosen interactively.

## Marketplace config

Copy `.env.example` → `.env` and fill in URLs + local paths for your public and private plugin marketplaces. Then run `/refresh-indexes` (or `python3 scripts/refresh_indexes.py`) to cache the plugin/skill indexes to `~/.local/share/claude-skill-definer/` (override via `CSD_DATA_DIR`). The installer reads these caches to resolve `plugin:<name>` targets.

Sanity check with `python3 scripts/csd_config.py check`.

## Typical flow

```
inbox/voice/record-a-video.m4a
  → transcribe (gemini MCP)
  → specs/record-a-video.md   (normalized process)
  → skills-staged/record-a-video/SKILL.md
  → install → ~/repos/.../plugin/skills/record-a-video/
```

## Status

Early scaffolding. Agents and commands are stubs — intake pipeline and `SKILL.md` authoring conventions are the first thing to harden.
