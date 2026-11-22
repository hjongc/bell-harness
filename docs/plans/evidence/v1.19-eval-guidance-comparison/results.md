# Offline judge preflight

Run from the repository root.

```sh
python3 docs/plans/evidence/v1.19-eval-guidance-comparison/judge.py --self-check
```

The exit code was 0 and the final line was `JUDGE: 4/4 controls matched`. The starters serve as known-bad controls and the reference files overlay only the allowed implementation files.

| Task | Check | Starter | Valid reference |
| --- | --- | --- | --- |
| Preview | Installed launch from outside the source tree | Pass, exit 0 | Pass, exit 0 |
| Preview | Different installed and source templates with a non-ASCII title | Fail, installed template absent and fallback output | Pass, installed bytes preserved and expected output |
| Preview | Missing installed template | Fail, apparent success | Pass, exit 2, diagnostic and empty stdout |
| Receipts | First event | Pass, exit 0, one receipt | Pass, exit 0, one receipt |
| Receipts | Repeated ID with a changed payload | Fail, second invocation changed state bytes | Pass, exit 0, original bytes unchanged |
| Receipts | Distinct event | Pass, two ordered entries | Pass, two ordered entries |
| Receipts | Malformed JSON with existing state | Pass, exit 2, bytes unchanged | Pass, exit 2, bytes unchanged |
| Receipts | Invalid object schema with existing state | Pass, exit 2, bytes unchanged | Pass, exit 2, bytes unchanged |
| Receipts | Malformed JSON with absent state | Pass, exit 2, file remains absent | Pass, exit 2, file remains absent |

The controls show that the preflight accepts both reference implementations and catches ordinary-variant failures after each starter passes its simple case. This covers the behavior of the judge. The effect of the guidance on newly produced work is pending the live comparison.

The [protocol](protocol.md) describes the matched session order and review. [Input hashes](inputs.sha256) freeze the judge, tasks and overlays.

## Repository verification

Direct judging of each starter returned exit 1. All ten frozen files matched their recorded hashes before and after judging, and all frozen Python files parsed with Python 3.9 syntax. The final `scripts/check` exited 0 with `Ran 106 tests in 57.675s (4 workers)` and `GUARD: real home unchanged`.
