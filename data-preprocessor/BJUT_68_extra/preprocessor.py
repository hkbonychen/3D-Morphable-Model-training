import csv
import sys
import os
import subprocess
import numpy as np
from pathlib import Path

#current config: 1000 or 1
scale = 1000
z_offset = -0.120*scale

def walklevel(some_dir, level=0):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]

def getXYZID(row):
	x=0
	y=0
	z=0
	lmID=0
	if (row[0].lstrip() == '<point x='): 
		x = str("{0:.6f}".format(float(row[1]) * scale))
	if (row[0].lstrip() == '<point y='): 
		y = str("{0:.6f}".format(float(row[1]) * scale))
	if (row[0].lstrip() == '<point z='): 
		z = str("{0:.6f}".format(float(row[1]) * (-1) * scale + z_offset))
	if (row[0].lstrip() == '<point name='):		
		lmID = str(row[1])
	for i in range(2,10,2):		
		if (row[i].lstrip() == 'x='): 
			x = str("{0:.6f}".format(float(row[i+1]) * scale))
		if (row[i].lstrip() == 'y='): 
			y = str("{0:.6f}".format(float(row[i+1]) * scale))
		if (row[i].lstrip() == 'z='): 
			z = str("{0:.6f}".format(float(row[i+1]) * (-1) * scale + z_offset))
		if (row[i].lstrip() == 'name='):			
			lmID = str(row[i+1])
	return [x, y, z, lmID]

if __name__ == '__main__':	

	#get folder name, and store them into a list
	directory_list = list()
	path = os.getcwd()
	for r, d, f in walklevel(path):
		for folder in d:
			directory_list.append(os.path.join(r, folder))

	for path in directory_list:					
		#check if the resulting files (obj and landmark files) exist in output directory
		#if exist, cp to lsfm input directory and skip the modification process
		obj_name = os.path.basename(os.path.normpath(path))		
		final_landmark = path + '/output/' + obj_name + ".obj.landmark"		
		landmark_in = path + '/' + os.path.basename(os.path.normpath(path)) + '_picked_points.pp'
		#preprocess the .pp file 
		command = 'sed -i "/templateName/d" ' + landmark_in
		os.system(command)
		if not Path(final_landmark).exists():		
			#create output directory to store the resulting obj and landmark file
			os.system('mkdir ' + path + '/output')

			start = False			
			with open(landmark_in) as pp_file:
				with open(path + '/output/' + obj_name + '.obj.landmark', "w") as csv_writer:
					pp_file = csv.reader(pp_file, delimiter='"')	
					for row in pp_file:
						#print(row[0].lstrip())
						if start:
							if row[0].lstrip() != '</PickedPoints>':	
								xyz = getXYZID(row)
								#print(xyz[0])
								csv_writer.write(xyz[0] + " " + xyz[1] + " " + str(float(xyz[2])) + " " + xyz[3] + "\n")
						if row[0].lstrip() == '</DocumentData>':
							start = True
			result = subprocess.call(["sort",  "-n",  "-k4", final_landmark, "-o", path + '/output/temp.landmark'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
			temp_landmark = path + '/output/temp.landmark'
			command = 'cut -d " " -f 1-3 ' + temp_landmark + ' > ' + final_landmark
			os.system(command)
			result = subprocess.call(["rm", temp_landmark], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)			
