import csv
import sys

scale = 100
x_offset = 0
y_offset = 0
z_offset = 0

obj_in = sys.argv[1] + '.obj'
data = []
with open( obj_in ) as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=' ')
	for row in csv_reader:
		data.append(row)
1000
for row in range(len(data)):
	if (data[row][0] == 'v'):
		data[row][1] = "{0:.6f}".format(float(data[row][1]) * scale + x_offset)
		data[row][2] = "{0:.6f}".format(float(data[row][2]) * (-1) * scale + y_offset)
		data[row][3] = "{0:.6f}".format(float(data[row][3]) * (-1) * scale + z_offset)

obj_out = sys.argv[1] + '_new.obj'
with open(obj_out, 'w', newline='') as csvfile:
	writer = csv.writer(csvfile,  delimiter=' ')
	writer.writerows(data)
