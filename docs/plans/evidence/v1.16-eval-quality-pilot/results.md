# Outcome-check pilot results

Run from the repository root.

```sh
python3 docs/plans/evidence/v1.16-eval-quality-pilot/replay.py
```

The replay copies each historical parser from Git and invokes it as `python3 <temporary-script-directory>/decisions.py <temporary-project>`. Each invocation gets its own temporary project with the same synthetic input for that case.

| Revision | Valid one line | Valid wrapped | Valid wrapped with nested notes | Missing required field |
| --- | --- | --- | --- | --- |
| `92e3bca` before fix | 0 | 1 | 1 | 1 |
| `83713c5` initial fix | 0 | 0 | 1 | 1 |
| `3cbb76b` follow-up | 0 | 0 | 0 | 1 |

The original wrapped case passed on both fixes. The nested variant identified a remaining defect in the initial fix, which exited 1 with `by must be 'user' or 'observed'`. The follow-up passed that variant. All three revisions rejected the invalid control with `missing field 'by'`.

```text
REPLAY: 12/12 cases matched and kept their input unchanged
```

The replay exited 0. Every sample file stayed byte-for-byte identical after its check. A fresh empty Git repository gave exit 1 with a missing-revision diagnostic. Changing one expected exit in memory gave exit 1 and reported 11 of 12 matches.

The replay supports adding the agreed ordinary-variant sentence to step 3 of the existing eval skill. The evidence covers outcome discrimination on these public historical versions and inputs. The proposed v1.19 comparison covers the separate question of whether the guidance improves newly produced deliverables.
