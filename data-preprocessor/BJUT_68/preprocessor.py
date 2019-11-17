import csv
import sys
import os
import subprocess
import numpy as np
from pathlib import Path
import random

#current config: 1000 or 1
scale = 1000
z_offset = -0.120*scale
#z_offset = 0*scale

def walklevel(some_dir, level=0):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]

def remap_landmark(id):
	remap_table = [16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 27, 28, 29, 30, 35, 34, 33, 32, 31, 45, 44, 43, 42, 47, 46, 39, 38, 37, 36, 41, 40, 54, 53, 52, 51, 50, 49, 48, 59, 58, 57, 56, 55, 64, 63, 62, 61, 60, 67, 66, 65]
	return remap_table[id]

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
		lmID = str(remap_landmark(int(row[1])))
	for i in range(2,10,2):		
		if (row[i].lstrip() == 'x='): 
			x = str("{0:.6f}".format(float(row[i+1]) * scale))
		if (row[i].lstrip() == 'y='): 
			y = str("{0:.6f}".format(float(row[i+1]) * scale))
		if (row[i].lstrip() == 'z='): 
			z = str("{0:.6f}".format(float(row[i+1]) * (-1) * scale + z_offset))
		if (row[i].lstrip() == 'name='):			
			lmID = str(remap_landmark(int(row[i+1])))		
	return [x, y, z, lmID]

def main():
	#get folder name, and store them into a list
	directory_list = list()
	path = os.getcwd()
	train_set_f = open(sys.argv[1] + '/training_set.txt', 'w')
	verification_set_f = open(sys.argv[1] + '/verification_set.txt', 'w')
	precentage = float(sys.argv[2])
	for r, d, f in walklevel(path):
		for folder in d:
			directory_list.append(os.path.join(r, folder))

	for path in directory_list:			
		obj_name = os.path.basename(os.path.normpath(path))
		ply_in = path + '/' + os.path.basename(os.path.normpath(path)) + '.ply'
		#check if the resulting files (obj and landmark files) exist in output directory
		#if exist, cp to lsfm input directory and skip the modification process
		lsfm_inputDir = sys.argv[1]
		final_obj = path + '/output/' + obj_name + ".obj"
		final_ply = path + '/output/' + obj_name + ".ply"
		final_landmark = path + '/output/' + obj_name + ".obj.landmark"		
		if Path(final_obj).exists() and Path(final_landmark).exists():
			final_landmark_count = 0
			with open(final_landmark) as landmark_file:
				for row in landmark_file:
					final_landmark_count = final_landmark_count + 1
			if final_landmark_count == 68:
				if (random.random() <= precentage):
					os.system('cp ' + final_obj + ' ' + lsfm_inputDir + '/training_set')
					os.system('cp ' + final_landmark + ' ' + lsfm_inputDir + '/training_set')
					train_set_f.write(obj_name + '\n')
				else:
					os.system('cp ' + final_obj + ' ' + lsfm_inputDir + '/verification_set')
					os.system('cp ' + final_landmark + ' ' + lsfm_inputDir + '/verification_set')
					verification_set_f.write(obj_name + '\n')			
		else:
			data = []
			numOfVertices = 0
			count = 0
			flag = False	
			#create output directory to store the resulting obj and landmark file
			os.system('mkdir ' + path + '/output')

			with open( ply_in ) as csv_file:
				csv_reader = csv.reader(csv_file, delimiter=' ')
				for row in csv_reader:
					data.append(row)
					#if ((row[0] == 'property') and 
					#	((row[2] == 'nx') or (row[2] == 'ny') or (row[2] == 'nz') or 
					#	(row[2] == 'red') or (row[2] == 'green') or (row[2] == 'blue') or
					#	(row[2] == 'alpha'))):				
					#	data.pop()


			for row in range(len(data)):
				if (data[row][0] == 'element') and (data[row][1] == 'vertex'):
					numOfVertices = int(data[row][2])	
				if flag and count < numOfVertices:
					data[row][0] = "{0:.6f}".format(float(data[row][0]) * scale)
					data[row][1] = "{0:.6f}".format(float(data[row][1]) * scale)
					data[row][2] = "{0:.6f}".format(float(data[row][2]) * (-1) * scale + z_offset)
					count = count + 1
				elif flag and count >= numOfVertices:
					if data[row][0] == '3':
						face_1 = data[row][1]
						face_2 = data[row][2]
						data[row][1] = face_2
						data[row][2] = face_1
				if (data[row][0] == 'end_header'):
					flag = True				

			with open('temp.ply', 'w', newline='') as csvfile:
				writer = csv.writer(csvfile,  delimiter=' ')
				writer.writerows(data)

			output_file = path + '/output/' + obj_name + '.obj'
			result = subprocess.call(["/home/u/workspace/Utilities/pcl-pcl-1.9.1/build/bin/pcl_ply2obj", "temp.ply", output_file], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)			

			start = False
			landmark_in = path + '/' + os.path.basename(os.path.normpath(path)) + '_68.pp'
			landmark_count = 0
			with open(landmark_in) as pp_file:
				with open(path + '/output/' + obj_name + '.obj.landmark', "w") as csv_writer:
					pp_file = csv.reader(pp_file, delimiter='"')	
					for row in pp_file:
						#print(row[0].lstrip())						
						if start:
							if row[0].lstrip() != '</PickedPoints>':	
								xyz = getXYZID(row)
								landmark_count = landmark_count + 1
								#print(xyz[0])
								csv_writer.write(xyz[0] + " " + xyz[1] + " " + str(float(xyz[2])) + " " + str(xyz[3]) + "\n")
						if row[0].lstrip() == '</DocumentData>':
							start = True
			result = subprocess.call(["sort",  "-n",  "-k4", final_landmark, "-o", path + '/output/temp.landmark'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
			temp_landmark = path + '/output/temp.landmark'
			command = 'cut -d " " -f 1-3 ' + temp_landmark + ' > ' + final_landmark
			os.system(command)
			result = subprocess.call(["rm", temp_landmark], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
			result = subprocess.call(['cp', 'temp.ply', final_ply])
			result = subprocess.call(["rm", "temp.ply"], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
			if landmark_count == 68:
				if (random.random() <= precentage):
					result = subprocess.call(['cp', final_obj, lsfm_inputDir + '/training_set'])
					result = subprocess.call(['cp', final_landmark , lsfm_inputDir + '/training_set'])
					train_set_f.write(obj_name + '\n')
				else:
					result = subprocess.call(['cp', final_obj, lsfm_inputDir + '/verification_set'])
					result = subprocess.call(['cp', final_landmark , lsfm_inputDir + '/verification_set'])		
					verification_set_f.write(obj_name + '\n')
	train_set_f.close()
	verification_set_f.close()


if __name__ == '__main__':
	main()
