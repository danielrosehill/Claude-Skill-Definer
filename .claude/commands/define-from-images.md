---
description: Turn paired images + text in inbox/ into a process spec.
---

Invoke the `image-text-fusor` agent.

If $ARGUMENTS is empty, scan `inbox/images/` and `inbox/text/` for basename pairs and list them.
Otherwise treat $ARGUMENTS as a basename (match `.png/.jpg/.jpeg` in images/ and `.md/.txt` in text/).

Flag any unpaired images or text files so the user can decide what to do with them.
