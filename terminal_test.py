import os, sys, time
import subprocess, signal

py = sys.executable
print(py)
child = subprocess.Popen([py, 'storj.py'],
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         preexec_fn=os.setsid)

input('enter any key')
os.killpg(child.pid, signal.SIGTERM)
