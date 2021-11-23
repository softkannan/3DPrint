#	Hier Accel anpassen bitte

# Der KISS postprocessor aus dem letzten Jahr mit mehr Optionen aus dem letzten Jahr in neuer Version. Keine Ahnung ob es jemand verwendet, einfach mal hier rein.

# Pfade bitte anpassen je nach Python Position und Script Position. bei Printer->Firmware->Post-Process
# Haken setzen bei "include comments" (danke für den Hinweis)
# C:\Users\Stephan\AppData\Local\Programs\Python\Python38-32\python.exe C:\Users\Stephan\Desktop\Kisslicer\kiss_pp.py <FILE>

accels = {
	'Top layer': 2000 ,			#	Accell der oberen Objektdecke

	'Perimeter Path': 2000 ,	#	Aussenwand und loop 1
	'Loop Path': 3000 ,			#	loop 2 bis loop n
	
	'Infill Path': 6000 ,		#	sparse infill - das mit den Prozenten
	'Solid Path': 6000 , 		#	Solides infill - Die richtigen "decken" und "böden"
	
	'Travel Path': 6000 ,		#	betrifft beides den Eilgang
	'Destring Suck': 6000 ,

	'Crown Path': 3000			#	Dünne Wände zum füllen von lücken
}

#	set your extrusion multiplers here

extrusion ={
	'Perimeter Path': 1 ,		#	Aussenwand und loop 1
	'Loop Path': 1.03 ,			#	loop 2 bis loop n
	
	'Infill Path': 1 ,			#	sparse infill - das mit den Prozenten
	'Solid Path': 1 , 			#	Solides infill - Die richtigen "decken" und "böden"

	'Crown Path': 1.06			#	Dünne Wände zum füllen von lücken
}

############################################################################
############################################################################

import sys

#
src_file = sys.argv[1]
#
try:
	gcode = []
	with open( src_file , 'r' ) as fp:  
		for cnt, line in enumerate(fp):
			gcode.append( line )
except Exception as e:
	raise e
	time.sleep(20)

top_on = [ 'TopLoop', 'TopPerimeter', 'TopSolid' ]
top_off = [ 'Prepare for End-Of-Layer', 'Prepare for Perimeter' ]
toplayer = False
allkeys = accels.keys()
extr_mult = 1
output = []

for l in gcode:

	#	find extrusion typus
	if any(x in l for x in allkeys):
		h = [ key for key in allkeys if key in l ][0]
		accel_target = accels[h]
		extr_mult = extrusion.get(h, 1)

	#	trigger toplayer on
	if any(x in l for x in top_on):
		toplayer = True
		#output.append('; \t\t\t\t\t\t\t\t\t\t\t\t\t\t toplayer_toggle: ' + str(toplayer) + '\n')
	#	trigger toplayer off
	if any(x in l for x in top_off):
		toplayer = False
		#output.append('; \t\t\t\t\t\t\t\t\t\t\t\t\t\t toplayer_toggle: ' + str(toplayer) + '\n')
	#	overwrite accel if this is toplayer
	if toplayer and h != 'Destring Suck':
		output.append('; toplayer_state: ' + str(toplayer) + '\n')
		accel_target = min( accel_target, accels['Top layer'] )
	#	apply accel
	if l.startswith( '; head speed' ):
		output.append( 'SET_VELOCITY_LIMIT ACCEL=' + str(accel_target) + ' ACCEL_TO_DECEL=' + str(accel_target) + ' SQUARE_CORNER_VELOCITY=5\n' )
	#	apply extrusion
	if l.startswith( 'G1 X' ) and extr_mult != 1:
		if extr_mult != 1:
			items = l.split(' ')
			for i in range(0,len(items)):
				if items[i].startswith('E'):
					items[i] = 'E' + str( round( float( items[i][1:] ) * extr_mult, 6 ))
			l = ' '.join(items) + '\n' # l + ' ; change:' + ' '.join(items) + '\n'

	output.append(l)
#with open( sys.argv[1] , 'w') as f:
with open( sys.argv[1] , 'w') as f:
	for line in output:
		f.write(line)
