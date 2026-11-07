This repository hosts OMEGA NEXT update assets and a verified release workflow.

To publish a new version, add `releases/vX.Y.Z/omega-update.zip.b64`
and (optionally) `releases/vX.Y.Z/notes.md` on `main`.
The GitHub Action will validate and publish the decoded `omega-update.zip`.

Never commit saves, credentials, private keys, or personal conversations.
The first update must be a real version **newer than 3.0.0**.
