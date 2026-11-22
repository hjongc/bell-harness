# Offline check profile

## Method

Use one checkout with the v1.16 and v1.17 changes in place. Run the existing `scripts/check` main sequentially with worker counts 4, 4 and 1. A temporary Python launcher imported the unchanged entry point, timed unittest module-suite execution by worker, and timed `Fixture.__init__` in the same workers. The timing hooks recorded outside the checkout and preserved Python startup, the home guard and all test inputs. Wall time covers the check process from launch to exit. Suite intervals are offsets from that launch.

```sh
python3 <temporary-directory>/launch.py --root . --output <temporary-directory>/baseline 4 4 1
# Arguments given to the original check entry point, in order:
scripts/check --jobs 4
scripts/check --jobs 4
scripts/check --jobs 1
```

All three runs exited 0, passed the same 106 test IDs and printed `GUARD: real home unchanged`. SHA-256 of the sorted test IDs joined with newlines was `48d631774398e6a75188829a447fa02e6049d2631c2c256b19d232480d0ba2fb` in all three runs.

## Results

| Profile | Wall | Runner | `test_doctor` fixture time (17 fixtures) | `test_setup` fixture time (22 fixtures) |
| --- | ---: | ---: | ---: | ---: |
| Four workers 1 | 53.038 s | 52.803 s | 7.298 s | 9.688 s |
| Four workers 2 | 52.920 s | 52.718 s | 7.555 s | 9.668 s |
| Serial | 127.276 s | 126.895 s | 6.373 s | 8.449 s |

| Profile | Last suite | Last suite interval | Previous worker completion | Last worker alone |
| --- | --- | ---: | ---: | ---: |
| Four workers 1 | `test_doctor` | 0.333–52.967 s | 46.179 s, `test_setup` | 6.788 s |
| Four workers 2 | `test_doctor` | 0.298–52.848 s | 46.344 s, `test_setup` | 6.505 s |

Another worker was already idle by 12.933 seconds in sample 1 and 11.294 seconds in sample 2. In the serial run, the three longest suites were `test_evals` at 40.346 seconds, `test_doctor` at 40.305 seconds, and `test_setup` at 34.379 seconds.

## Decision

Keep the current fixture and runner. On the last worker of the two parallel runs, fixture construction accounted for 13.76 percent and 14.28 percent of full wall time. Both samples are below the 20 percent threshold for a fixture prototype. The recorded times do not estimate a full-run improvement from reuse.

The repeated single-worker tail points to a separate scheduling candidate. `DoctorTests` creates and cleans its own temporary directory and fixture for each test. It defines no class or module fixtures. A later comparison could time individual methods and group them across two workers with full-install cases distributed, preserving test IDs, test-local state and the normal behavior of suites with shared fixtures.

The final uninstrumented `scripts/check` exited 0 with `Ran 106 tests in 57.238s (4 workers)` and `GUARD: real home unchanged`.
