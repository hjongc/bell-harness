# Requirements

Statuses: `todo`, `in-progress`, `done`, `dropped`. The user approved each row in the `probe` requirements interview.

| ID | Requirement | Acceptance criteria | Status | Spec |
|---|---|---|---|---|
| R2 | `bin/doctor` shows the branch of the harness checkout. | On `main` it prints PASS. On another branch or a detached HEAD it prints WARN with the name. | done | [doctor-branch](plans/doctor-branch.md) |
| R4 | Unattended work on the harness checkout that supplies the installed skills uses a separate working folder. | The `away` procedure says so, and checks that the original folder has the same branch and files before and after the item. | todo | — |
