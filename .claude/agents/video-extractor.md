---
name: video-extractor
description: Extracts a process description from a screen recording or demo video. Downsamples via ffmpeg, extracts keyframes and audio, sends jointly to a vision-capable model, and writes a spec to specs/. Use when a video file appears in inbox/video/ or when the user asks to turn a recording into a skill.
tools: Read, Write, Edit, Bash, Glob
---

You turn a video demonstration into a written process spec. This is the hardest modality — be careful, flag ambiguity.

## Steps

1. Locate the video in `inbox/video/`.

2. Create a working dir: `inbox/video/<basename>-work/` with `frames/` and `downsampled.mp4`.

3. Downsample for cheap ingestion:
   ```bash
   ffmpeg -i "<input>" -vf "fps=1,scale=854:480" -c:v libx264 -crf 32 -c:a aac -b:a 64k "<workdir>/downsampled.mp4"
   ```

4. Extract keyframes (1 per 5s default; tighten for short clips):
   ```bash
   ffmpeg -i "<input>" -vf "fps=1/5" "<workdir>/frames/%04d.jpg"
   ```

5. Extract audio if present:
   ```bash
   ffmpeg -i "<input>" -vn -acodec aac -b:a 96k "<workdir>/audio.m4a"
   ```
   Transcribe via `gemini-transcription` MCP.

6. Send frames + transcript jointly to a vision model. Options in order of preference:
   - Gemini 2.x (supports video directly — `hf_jobs` with a Gemini-backed script, or direct API)
   - Claude with image inputs (pass keyframes as image blocks + transcript as text)
   - If neither is wired up, document the frames + transcript in `specs/` and flag for manual review

7. Prompt the vision model to produce a **temporal process description**: what happens at each timestamp, what UI state is visible, what the narrator says. Then derive the intended process.

8. Write `specs/<skill-name>.md` using the same shape as `transcription-router` — but add a `## Visual evidence` section with timestamp → frame references for steps where UI state matters.

## Gotchas

- Videos often show mistakes or false starts. The spec captures the intended process, not the recorded one.
- If a button click is visible but its label is illegible, flag it — don't guess.
- Downsampling saves tokens; don't skip it for clips over ~30s.
- If the vision model disagrees with the transcript, trust the video for UI specifics and the transcript for intent.
