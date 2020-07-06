import sys
import os
import numpy as np
import re

if '-nograph' in sys.argv:
	pass
else:
	import matplotlib.pyplot as plt

#########################################################################################################################################
#	Script for Knauer ASCII-file input		                        							#
#	----------------------------------				         							#
#										                                            		#
#	The script converts ASCII-files from EZCHROM into two .txt files (UV and Fluorescence) with time and volume data. Both 		#
#	curves are plotted and saved as .png file. The script handles two curves, but can be extended to handle more.		    	#
#											                                                # 
#	Dependencies: Matplotlib, use without graph output (-nograph) in case.					              		#
#								                                                    			#
#	Usage: Copy fhplc.py to folder with ASCII files (.asc) and run script. Only files within the same folder will be processed. 	#
#													                		#
#	Essential arguments:	-f flow rate in ml/min (i.e. "python fhplc.py -f 0.25")					                #
#	Optional arguments: 	-notxt (no .txt file output) 		            							#
#							-nograph (no graph output)	                    				#
#							-dpi 500 (for specific resolution, 200 standard)	              		#
#														                     	#
#########################################################################################################################################

def is_number(s):   ##### definition to check for floats
	try:
		float(s)
		return True
	except ValueError:
		return False

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_png = dir_path + '/png'
if not os.path.exists(dir_png):
	os.makedirs(dir_png)

dir_txt = dir_path + '/txt'
if not os.path.exists(dir_txt):
	os.makedirs(dir_txt)


i = 1
while i <= len(sys.argv)-1:  ##### Flow rate input as first argument, convert to float
	if '-f' in sys.argv[i]:
		if is_number(sys.argv[i+1]):
			flow = float(sys.argv[i+1])
			print('Flow rate: '+str(flow)+' ml/min\n')
		else:
			print("Flow rate not properly set! Usage: -f 0.5 (in ml/min)\n")
			print("Script quit\n")
			quit()
		break
	else:
		if i == len(sys.argv)-1:
			print("Flow rate not set! Usage: -f 0.5 (in ml/min)\n")
			print("Script quit\n")
			quit()
		i+=1

try:
	flow
except NameError:
	print ("Please set flow rate properly! Usage: -f 0.5 (in ml/min)\n")
	print ('Exit!')
	quit()

if '-notxt' in sys.argv:
	print("Omit text file output.\n")

if '-nograph' in sys.argv:
	print("Omit graph output.\n")


i = 1
while i <= len(sys.argv)-1:  ##### check for dpi argument
	if '-dpi' in sys.argv[i]:
		if is_number(sys.argv[i+1]):
			dpi = int(sys.argv[i+1])
		else:
			break
		break
	else:
		i+=1

files = [g for g in os.listdir('.') if os.path.isfile(g)]  ##### check for files in same folder
files = np.sort(files, axis=0)

##### definitions for progress bar
number = 0
progress = 1.0
percent = 0
bar_length = 50
#####

for g in files:   #### count ascii files in folder
	if '.asc' in g:
		number += 1
print('Number of ASCII files to process: %d\n' %number)

if number == 0:
	print('No files to process!\n')
	print('Exit!')
	quit()

for g in files:   #### data manipulation routine
	if '.asc' in g:
		data = []

		minutes1 = []
		volume1 = []
		data1 = []

		minutes2 = []
		volume2 = []
		data2 = []

		nr = 0
		f = open(g, 'r')
		for line in f:
			line = line.replace(',','.')
			if 'Sample ID:' in line:
				splitline = line.split()
				splitline.pop(0)
				splitline.pop(0)
				sample = ' '.join(splitline)
			if 'Date and Time:' in line:
				splitline = line.split()
				date = splitline[4]
				time = splitline[5]
			if 'X Axis Title:' in line:
				splitline = line.split()
				xtitle = [splitline[3],splitline[4]]
			if 'Y Axis Title:' in line:
				splitline = line.split()
				ytitle = [splitline[3],splitline[4]]
			if 'Rate:' in line:
				rates=list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", line)))
			if 'Total Data Points:' in line:
				points=list(map(int, re.findall(r"[-+]?\d*\.\d+|\d+", line)))
			if 'X Axis Multiplier:' in line:
				xmulti=list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", line)))
			if 'Y Axis Multiplier:' in line:
				ymulti=list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", line)))
			if is_number(line):
				data = np.append(data, int(line))
		f.close()
		i=0
		while i < len(data):   ###### create arrays for time, volume and data
			if i < points[0]:
				time = (float(i)/float(points[0])*float(points[0])/rates[0]/60)
				minutes1 = np.append(minutes1,time)
				vol = time * flow
				volume1 = np.append(volume1,vol)
				data1 = np.append(data1,data[i]*ymulti[0])
			if i >= points[0]:
				time = ((float(i)-float(points[0]))/float(points[1])*float(points[1])/rates[1]/60)
				minutes2 = np.append(minutes2,time)
				vol = time * flow
				volume2 = np.append(volume2,vol)
				data2 = np.append(data2,data[i]*ymulti[1])
			i += 1

		if '-nograph' in sys.argv:
			pass
		else:
			plt.clf()
			fig, ax1 = plt.subplots() ###### Plotting

			ax2 = ax1.twinx()
			ax1.plot(volume1, data1, 'g-')
			ax2.plot(volume2, data2, 'b-')

			#fig.suptitle(sample, fontsize=12, fontweight='bold')

			ax1.set_xlabel('Volume (ml)')
			ax1.set_ylabel('Fluorescence'+' ('+ytitle[0]+')', color='g')
			ax2.set_ylabel('UV'+' ('+ytitle[1]+')', color='b')
			ax1.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.2)

			try:
				dpi
				plt.savefig(dir_png+'/'+sample, dpi=dpi)
			except NameError:
				plt.savefig(dir_png+'/'+sample, dpi=200)
			plt.close()
		if '-notxt' in sys.argv:
			pass
		else:
			set1 = np.column_stack((minutes1,volume1,data1))
			set2 = np.column_stack((minutes2,volume2,data2))

			with open(dir_txt+'/'+sample+'_Fluorescence.txt', 'wb') as h: ##### Output txt files for excel import
				h.write(b'time(min), volume(ml), data('+(ytitle[0].encode("UTF-8"))+b')\n')
				np.set_printoptions(precision=3)   
				np.savetxt(h, set1, fmt='%10.3f',delimiter=',')
			h.close()

			with open(dir_txt+'/'+sample+'_UV.txt', 'wb') as j: ##### Output txt files for excel import
				j.write(b'time(min), volume(ml), data('+(ytitle[1].encode("UTF-8"))+b')\n')
				np.set_printoptions(precision=3)   
				np.savetxt(j, set2, fmt='%10.3f',delimiter=',')
			j.close()

		percent = (progress/number) ##### Progress bar
		hashes = '#' * int(round(percent * bar_length))
		spaces = ' ' * (bar_length - len(hashes))
		sys.stdout.write("\rProgress: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
		sys.stdout.flush()
		progress +=1

##### End of routine

print('\n\nDone!\n')
