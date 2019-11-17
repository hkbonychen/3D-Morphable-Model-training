import pickle
import sys

in_filename = sys.argv[1] + '.pkl'
fin = open(in_filename, 'rb')
data = pickle.load(fin)
fin.close()

out_filename = sys.argv[1] + '.ply'
num_points = int(len(data)/3)
header = '''ply
format ascii 1.0
comment UNRE generated
element vertex {0}
property float x
property float y
property float z
element face 0
property list uchar int vertex_indices
end_header\n'''.format(num_points)

with open(out_filename, 'w') as fout:
	fout.writelines(header)
	for idx in range(0, num_points):
		fout.write(str(data[idx*3+0]))
		fout.write(' ')
		fout.write(str(data[idx*3+1]))
		fout.write(' ')
		fout.write(str(data[idx*3+2]))
		fout.write('\n')
fout.close()



