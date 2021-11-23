# Travel accels setzen im Susl für Klipper. Da die Extrusion_role dort nicht existiert.
# starten mit "OUTPUT OPTIONS" im print tab( Beispiel)

# C:\Users\Stephan\AppData\Local\Programs\Python\Python38-32\python.exe C:\Users\Stephan\Desktop\SS-master-11.08\pp.py;

import sys, re, time

#############
#	accel, acceltodecel, squarecorner
travel = [ 6000, 6000, 5 ]

#############
output = []

target = travel
saved = [ 0, 0, 0 ]
last = [ 0,0,0 ]

untrigger = False

gcode = open(sys.argv[1], 'r')
content = gcode.read()

alltravels = re.findall('G1 X\d+.\d+ Y\d+.\d+ F(\d+.\d+?)', content)
travelspeed = str(max([ float(x) for x in  alltravels ]))

try:
	with open( sys.argv[1] , 'r' ) as fp:  
		for cnt, line in enumerate(fp):

			#	pick existing accel
			if "SET_VELOCITY_LIMIT" in line:
				numbers = re.findall(r'\d+', line)
				target = last = saved = [ numbers[0] , numbers[1] , numbers[2] ]

			if travelspeed in line:
				target = travel
				untrigger = True

			if untrigger and re.match('G1 F\d+', line):
				target = saved
				untrigger = False

			if target != last:
				output.append("SET_VELOCITY_LIMIT ACCEL=" + str(target[0]) + " ACCEL_TO_DECEL=" + str(target[1]) + " SQUARE_CORNER_VELOCITY=" + str(target[2]) + "\n")
				last = target

			output.append(line)

except Exception as e:
	print(e)
	time.sleep(200)


#	overwrite original file
with open( sys.argv[1] , 'w') as f:
	for line in output:
		f.write(line)