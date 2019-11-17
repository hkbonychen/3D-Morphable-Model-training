import sys
import os
import subprocess
from pathlib import Path

def walklevel(some_dir, level=0):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]

#get folder name, and store them into a list
directory_list = list()
path = os.getcwd()
for r, d, f in walklevel(path):
	for folder in d:
		directory_list.append(os.path.join(r, folder))

for path in directory_list:
	result = subprocess.call(['rm', '-rf', path + '/output'])

if Path('temp.ply').exists():
	result = subprocess.call(['rm', 'temp.ply'])
