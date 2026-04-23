---
description: Turn a screen recording / demo video in inbox/video/ into a process spec.
---

Invoke the `video-extractor` agent on the target video.

If $ARGUMENTS is empty, list `inbox/video/` and ask.
Otherwise treat $ARGUMENTS as the filename.

Warn the user that video processing takes longer and costs more tokens (frames + transcript sent jointly to a vision model). Confirm before starting if the video is over 5 minutes.
