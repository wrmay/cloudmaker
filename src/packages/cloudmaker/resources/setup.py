import os
import os.path
import subprocess
import sys

#this script will be run in /tmp/setup.  It will simply iterate through
#the subdirectories in alphabetical order, "cd" to each and run setup.py

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(sys.argv[0]))
    dirs = os.listdir(here)
    dirs.sort()
    for name in dirs:
        dir = os.path.join(here, name)
        if os.path.isdir(dir):
            subprocess.check_call(['python','setup.py'],cwd=dir)