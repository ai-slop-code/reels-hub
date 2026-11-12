# Review packet 10: security engineer

**Priority:** before phase 0 (container) and phase 2 (MCP)
**Time needed:** ~1.5 h
**Decisions already made:** D4 local-only processing; D6 prompt injection out of scope; D7 dependencies accepted (see [README](README.md#decisions-already-made-please-dont-reopen)). Focus on the **local attack surface and safe defaults**, not on reopening these.

## Why you
Reels Hub runs a local server that AI agents can write to, holds an Instagram API token and mounts the media library. Defaults need to be safe even on a personal MacBook.

## Read
- [§17 Agent interface](../spec/REELS_HUB_SPEC.md#17-agent-interface-mcp-server): 17.3 agent rules
- [§11.3 Approval gate](../spec/REELS_HUB_SPEC.md#11-module-g-reviews-feedback-and-approvals)
- [§22 Security, privacy and safety](../spec/REELS_HUB_SPEC.md#22-security-privacy-and-safety)
- [§23 Deployment (Podman)](../spec/REELS_HUB_SPEC.md#23-deployment-podman)

## Questions
1. **MCP authentication:** token header on `127.0.0.1:8787`. Is that enough? Token rotation, per-agent tokens, read-only vs. write tokens?
2. **Approval gate:** export/publish refused without an approved version. How do we make it tamper-proof against an agent calling Edits directly (outside the Hub)?
3. **Container hardening:** rootless Podman, read-only root filesystem, dropped capabilities, which mounts must be writable, network egress needs.
4. **Secrets:** Podman secrets for the Meta token. Anything else to protect (Claude API keys if the critique calls models, Hugging Face token for pyannote)?
5. **Agent writes:** every write logged as a diff in `agent_log`. Is that enough to undo mistakes? Backups of the DB?
6. **Local web UI:** CSRF and DNS-rebinding protection for a localhost app.
7. **Updates:** pinning image and model versions, verifying downloads.

## Your input
<!-- Use the response format from the README. -->

**Sign-off:**
