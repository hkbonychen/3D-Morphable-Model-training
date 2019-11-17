import csv
import sys

ply_filename = sys.argv[2] + '.ply'
pp_filename = sys.argv[2] + '_lm.pp'
fo = open(pp_filename, "w")
header = '<!DOCTYPE PickedPoints> \n<PickedPoints> \n <DocumentData> \n  <DataFileName name="' + ply_filename + '"/> \n  <templateName name="' + sys.argv[2] + ' "/> \n </DocumentData>\n'
fo.write(header)
count = 1
with open(sys.argv[1]) as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=' ')
	for row in csv_reader:
		fo.write('\t<point x="' + row[0] + '" y="' + row[1] + '" z="' + row[2] + '" name="' + str(count) + '" active="1"/>\n')
		count = count + 1
fo.write('</PickedPoints>')
