import sys
import csv
import json
import numpy as np
import scipy.io

path = '/home/u/workspace/lsfm/output_dir/'

def getAlpha(json_file, ID):
	#read alpha from alpha.json
	with open(json_file) as f:
		alpha = json.load(f)
	alpha = np.array(list(map(float,alpha[ID])))
	return alpha

def getTargetModelAndTrilist(matlab_file, alpha):
	pca = scipy.io.loadmat(matlab_file)

	model = pca['mean'] + np.dot(alpha * np.sqrt(pca['eigenvalues']), pca['components'].T)
	return [model, pca['trilist']]

def exportPlyFile(file_out, model, trilist):

	header = '''ply
format ascii 1.0
comment UNRE generated
element vertex {0}
property float x
property float y
property float z
element face {1}
property list uchar int vertex_indices
end_header\n'''.format(int(len(model[0]) / 3), len(trilist))

	with open(file_out, 'w') as f:
		f.writelines(header)
		for idx in range(0, len(model[0]), 3):
			f.write(str(model[0][idx]))
			f.write(' ')
			f.write(str(model[0][idx + 1]))
			f.write(' ')
			f.write(str(model[0][idx + 2]))
			f.write(' ')
			f.write('\n')

		for idx in range(0, len(trilist)):
			f.write('3 ')
			for i in range(0, 3):
				f.write(str(int(trilist[idx][i])))
				f.write(' ')
			f.write('\n')

def main():
	alpha_json_file = path + 'pca_result/alpha.json'
	matlab_file = path + 'shape_model.mat'
	ply_file = path + 'recovered_ply/' + sys.argv[1] + '.ply'

	target_alpha = getAlpha(alpha_json_file, sys.argv[1])
	target_model, target_trilist = getTargetModelAndTrilist(matlab_file, target_alpha)
	exportPlyFile(ply_file, target_model, target_trilist)

if __name__ == '__main__':
	main()
