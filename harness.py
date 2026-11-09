"""Stress test for threads.py.

Runs the simulation N times and counts how many runs never finish (hangs).
A bug like a lost wakeup only shows up in a small fraction of runs, so one
run proves nothing; running it hundreds of times is how you catch it.

Usage: python3 harness.py [N] [TIMEOUT_SECONDS]
   e.g. python3 harness.py 1000      -> 1,000 runs, 15 s timeout each

Built by Claude
"""

import os
import subprocess
import sys

# If the user typed a number, use the number; otherwise, default to 300.
N = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
TIMEOUT = float(sys.argv[2]) if len(sys.argv) > 2 else 15

# Build the full path to threads.py, which lives in the same folder as this file.
# This way the harness works no matter which directory you run it from.
SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "threads.py")

hangs = 0     # runs that had to be killed
rounds = []   # rounds to converge, one entry per run that finished

for i in range(N):
    try:
        # Launch threads.py as its own separate Python process, the same as typing
        # "python3 threads.py" in a terminal. We do NOT import it, because:
        #   1. A deadlocked thread inside our own process would freeze the harness too,
        #      and it could never record the failure. A separate process can be killed.
        #   2. threads.py starts its threads as soon as it loads, so importing it
        #      would only ever run the simulation once.
        # capture_output=True collects everything the simulation prints, and
        # timeout=TIMEOUT kills the process if it runs too long.
        out = subprocess.run([sys.executable, SCRIPT], capture_output=True,
                             text=True, timeout=TIMEOUT).stdout

        # The central thread prints "Central Temperature:" once per round,
        # so counting that line tells us how many rounds this run took.
        rounds.append(out.count("Central Temperature:"))

    except subprocess.TimeoutExpired:
        # The run didn't finish in time, so a thread is stuck (deadlock)
        # or the threads never agreed they were done (livelock). Count it as a hang.
        hangs += 1

# Report the hang rate: this is the number that went from 1.5% to 0.
print(f"{hangs}/{N} runs hung ({100 * hangs / N:.1f}%)")

# Report how fast the runs that finished converged.
if rounds:
    rounds.sort()
    print(f"rounds to converge: median {rounds[len(rounds) // 2]}, max {rounds[-1]}")