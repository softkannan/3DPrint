# anlin 2020
import argparse
import os
import fnmatch
import re
import sys
from gooey import Gooey, GooeyParser

def glob_nocase(dir, filemask):
	if os.path.isfile(dir):
		return [dir]
	if not os.path.exists(dir):
		print("Directory not found ({0})".format(dir))
		return []
	rule = re.compile(fnmatch.translate(filemask), re.IGNORECASE)
	return [fname for fname in os.listdir(dir) if rule.match(fname)]
	
def replace_ext(filename, new_ext):
	return os.path.splitext(filename)[0]+"."+new_ext


def replace_retracts(input_path, output_path):
	infile = open(input_path, "r")
	outfile = open(output_path, "w")
	for line in infile:
		if(line == "; 'Destring Suck'\n"):
			outfile.write("; Firmware retract\nG10\n")
			next(infile) # Skip over the next line
		elif(line == "; 'Destring Prime'\n"):
			outfile.write("; Firmware deretract\nG11\n")
			next(infile) # Skip over the next line
		else:
			outfile.write(line)
	infile.close()
	outfile.close()
	return
	

def process_files(args):
	args.input = os.path.abspath(args.input)
	args.output = os.path.abspath(args.output)
	
	if os.path.isfile(args.input):
		single_file = True
		if args.output == "":
			args.output = replace_ext(args.input, "extrusion_removed.gcode")
		if os.path.isdir(args.output):
			args.output = os.path.join(args.output, replace_ext(os.path.basename(args.input), "extrusion_removed.gcode"))
	elif os.path.isdir(args.input):
		single_file = False
		if(args.output == ""):
			args.output = args.input
		if not os.path.isdir(args.output):
			print("Invalid output path")
			sys.exit(0)
	else:
		print("Invalid input path")
		sys.exit(0)
	
	gcode_paths = glob_nocase(args.input, "*.gcode")
	if(len(gcode_paths) == 0):
		print("No gcode files found")
		sys.exit(0)
	
	print("\nPreparing to process {0} files".format(len(gcode_paths)))
	for gcode in gcode_paths:
		in_path = args.input if single_file else os.path.join(args.input, gcode)
		out_path = args.output if single_file else os.path.join(args.output, replace_ext(gcode, "extrusion_removed.gcode"))
		replace_retracts(in_path, out_path)

	print("Done")

@Gooey
def main():
	parser = GooeyParser(description="Remove Gcode Extrude Moves")
	parser.add_argument("input", type=str, help="Input file/directory", widget='FileChooser')
	parser.add_argument("-out", dest="output", type=str, default="", help="Output file/directory", widget='FileChooser')	  
	args = parser.parse_args()
	process_files(args)

#############################################################s
if __name__=="__main__":
	main()