# Temperature Stabilization with Threads

A barrier-synchronization exercise in Python: one **central** thread and four **external** threads exchange temperatures in rounds until they all agree on one shared temperature. Built for an Operating Systems course by me, then stress-tested and fixed in 2026 assisted by Claude.

## How it works

Each round, every external moves toward the central temperature, then the central moves toward the average of everyone. The update formulas came from the assignment.

My part is the thread coordination: a **barrier** built from a shared counter and a `threading.Condition`. Each external checks in and sleeps; once all have checked in, the central updates and wakes them for the next round. A `stabilized` flag tells every thread when to stop.

## Bugs found and fixed

The original version worked in a single run but hung occasionally. A stress test exposed two separate shutdown bugs.

**1. Lost-wakeup deadlock.** Each external checked `stabilized` in its `while` condition, *before* taking the lock. If the central thread declared the system stable and called `notify_all()` in the gap between that check and `with condition:`, the external went on to `wait()` with nobody left to wake it, and the program never exited.

**Fix:** re-check `stabilized` right after acquiring the lock and `break` if it is already set. A decision about shared state is only valid while you hold the lock.

**2. Floating-point livelock.** The stop condition compared temperatures by snapping them to integers (`int()` and `round()`). When the system converged right on a boundary, for example 27.5, float error left some values at `27.500000000000007` and others at `27.499999999999993`. They rounded to 28 and 27, so the check never passed and the threads ran forever (one run was still going after 1,834 rounds).

**Fix:** compare actual distances. The run stops when both the coldest and the hottest external are within `threshold` of the central.

Smaller cleanups: replaced the hardcoded `4` and `6` with `numofthreads` so the thread count is configurable.

## Results

1,000 runs each, 15-second timeout per run:

| Version | Hung runs | Rounds to converge |
|---|---|---|
| Original | 15 / 1,000 (1.5%) | median 10, worst 72 |
| Fixed | **0 / 1,000** | median 9, worst 11 |

## Running it

```bash
python3 threads.py            # one simulation
python3 harness.py 1000       # stress test: 1,000 runs, reports hangs and rounds
```

Python 3, standard library only.
