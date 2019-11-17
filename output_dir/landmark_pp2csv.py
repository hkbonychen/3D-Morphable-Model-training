import csv
import sys

count = 0
with open(sys.argv[1]) as pp_file:
	with open(sys.argv[2], "w") as csv_writer:
		pp_file = csv.reader(pp_file, delimiter='"')	
		for row in pp_file:
			count = count + 1
			if count > 8 and count < 77:
				csv_writer.write(row[3] + " " + row[5] + " " + row[1] + "\n")
