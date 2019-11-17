import csv
import sys
import os
import subprocess
import numpy as np
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

sys.path.insert(0, '/home/u/workspace/python-utility') 
import hashtable

if __name__ == '__main__':	
	#example usage:
	#python3 preprocessor.py folder_A folder_B lsfm_input_dir
	#merge the landmark file from folder_B into folder_A for all the files exist in folder_A

	#get folder name, and store them into a list
	lsfm_inputDir = sys.argv[3]
	directory_list_1 = list()
	directory_list_2 = list()

	#instanatiate a hash table
	ht = hashtable.HashTable(10)

	#scan the directories to get the folder path
	for r, d, f in walklevel(sys.argv[1]):
		for folder in d:
			directory_list_1.append(os.path.join(r, folder))			

	for r, d, f in walklevel(sys.argv[2]):
		for folder in d:
			directory_list_2.append(os.path.join(r, folder))
			obj_name = os.path.basename(os.path.normpath(os.path.join(r, folder)))			
			ht.set(obj_name, True)

	for path in directory_list_1:
		obj_name = os.path.basename(os.path.normpath(path))
		#target file is the source to be copied
		target_obj_file = sys.argv[2] + obj_name + '/output/' + obj_name + '.obj'
		target_ply_file = sys.argv[2] + obj_name + '/output/' + obj_name + '.ply'
		target_landmark_file_1to68 = sys.argv[2] + obj_name + '/output/' + obj_name + '.obj.landmark'
		target_landmark_file_69to100 = sys.argv[1] + obj_name + '/output/' + obj_name + '.obj.landmark'		
		#final file is the destination of the file being copied
		final_obj_file = './' + obj_name + '/' + obj_name + '.obj'
		final_landmark_file = './' + obj_name + '/' + obj_name + '.obj.landmark'
		try: 
			if ht.get(obj_name):
				os.system('mkdir ' + obj_name)
				os.system('cp ' + target_obj_file + ' ' + './' + obj_name)
				os.system('cp ' + target_obj_file + ' ' + './' + obj_name)
				os.system('cat ' + target_landmark_file_1to68 + ' ' + target_landmark_file_69to100 + ' > ' + final_landmark_file)
		except KeyError:
			print("folder" + obj_name + " is not found in " + sys.argv[2])
		except:
			print('Unknow error in hash table search!')

		#copy the final files into the lsfm input directory
		landmark_count = 0
		with open(final_landmark_file) as final_lm_file:
			for row in final_lm_file:
				landmark_count = landmark_count + 1
		if landmark_count == 100:
			result = subprocess.call(['cp', final_obj_file, lsfm_inputDir])
			result = subprocess.call(['cp', final_landmark_file , lsfm_inputDir])
