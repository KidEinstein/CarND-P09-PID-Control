import os
import sys
import subprocess
import shlex
from threading import Timer

kill = lambda process: process.kill()

def run(p, speed=30, timeout=10):
    """Runs the PID app with the given gains."""
    cmd = shlex.split('./build/pid {0} {1} {2} {3}'.format(*p, speed))
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    my_timer = Timer(timeout, kill, [proc])
    lines = []
    avg_cte = float('inf')
    try:

        for line in proc.stdout:
            line = line.decode('ascii')
            if 'Connected' in line:
                my_timer.start()
                continue
            if 'cte ' not in line:
                continue
            cte = float(line.split()[1])
            if cte > 2.0:
                my_timer.cancel()
                kill(proc)

            lines.append(cte)
    finally:
        my_timer.cancel()

    if len(lines) > 0:
        avg_cte = sum(lines)/len(lines)
    return avg_cte

print(run([.1,.002,3.0]))
def twiddle(tol=0.001):
    p = [0.05, 0.0001, 1.5]
    dp = [.01, .0001, .1]

    best_err = run(p)

    it = 0
    while sum(dp) > tol:
        print("Iteration {}, best error = {}".format(it, best_err))
        for i in range(len(p)):
            p[i] += dp[i]
            err = run(p)

            if err < best_err:
                best_err = err
                dp[i] *= 1.1
            else:
                p[i] -= 2 * dp[i]
                robot = make_robot()
                x_trajectory, y_trajectory, err = run(robot, p)

                if err < best_err:
                    best_err = err
                    dp[i] *= 1.1
                else:
                    p[i] += dp[i]
                    dp[i] *= 0.9
        it += 1
    return p
