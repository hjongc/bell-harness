---
name: offline-verification
description: Use when asked to verify a built or installed artifact, or to exercise a real CLI or workflow offline with test data or fakes. Check the normal entry point and report what the offline run establishes.
---

# Offline verification

1. Read the active spec or project instructions. Identify the allowed commands, files, and side effects. Choose the smallest fixture that can exercise the requested behavior. Use a temporary home, isolated copy, or test double where the command would otherwise touch real state or an external service.
2. Run the normal entry point with that fixture. For a packaging check, use the built or installed artifact from a temporary directory outside the source checkout so source files cannot satisfy missing package files. When checking a boundary, exercise an allowed input and a rejected input. Compare relevant state before and after when the behavior promises a change or preservation.
3. Report the command, exit code, and relevant output or state observed. Keep secrets out of the report. Name any material check the offline fixture could not exercise, along with the permission or environment it would require.

During unattended work, record blocked checks and required approvals in `docs/plans/blocked.md`.

For example, check a read-only backup listing with a valid backup and a linked record in a temporary home. Verify the output, status code, and that the listed files and link target retain their contents.
