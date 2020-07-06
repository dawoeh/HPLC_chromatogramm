import sys
import os
import numpy as np
import re
from lmfit.models import GaussianModel, ExponentialModel
import matplotlib.pyplot as plt
import timeit

#########################################################################################################################################
#	Script for Knauer ASCII-file input												#
#	----------------------------------												#
#																	#
#	The script fits 4 gaussian curves to the data. It depends on matplotlib and lmfit. Change the parameters for the fit as  	#
#	needed. Fits are output as png-files in a separate folder. The Area below peak 2 is calculated and written into a single	#
#	txt-file for all input .asc files.												#
#																	#
#	Execute in folder with EZCHROM ASCII-files. Center and sigma of individual peaks should be modified in the script.		#
#																	#
#   	Arguments: 	-f 0.2 (flowrate in ml/min, essential)										#
#			-dpi 200 (200 default, higher possible, optional)								#								
#########################################################################################################################################

start_time=timeit.default_timer()

def is_number(s):   ##### definition to check for floats
	try:
		float(s)
		return True
	except ValueError:
		return False

def func(x, *params):
	y = np.zeros_like(x)
	for i in range(0, len(params), 3):
		ctr = params[i]
		amp = params[i+1]
		wid = params[i+2]
		y = y + amp * np.exp( -((x - ctr)/wid)**2)
	return y

######################################################

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

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_fit = dir_path + '/fit'
if not os.path.exists(dir_fit):
	os.makedirs(dir_fit)

#print dir_path

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

area=np.array([]).reshape(0,2)

for g in files:   #### data evaluation routine
	if '.asc' in g:
		data = []

		minutes1 = []
		volume1 = []
		data1 = []

		minutes2 = []
		volume2 = []
		data2 = []

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

		x = volume1			#####define values for fitting
		y = data1

		exp_mod = ExponentialModel(prefix='exp_')
		pars = exp_mod.guess(y, x=x)

		center = [1.8,2.2,2.9,3.5]  ### define center of expected peaks
		max_val = []

		i=0
		for h in center: ###determine starting amplitudes for fitting
			max_val = np.append(max_val,data1[np.where(x == h)])
			if max_val.size < (i + 1):
				max_val = np.append(max_val,data1[np.where(x == (h+0.01))])
			if max_val.size < (i + 1):
				max_val = np.append(max_val,data1[np.where(x == (h-0.01))])
			if max_val.size < (i + 1):
				max_val = np.append(max_val,np.amax(y)/5)
				print('Used artificial values for peak amplitues!')
			i+=1

		gauss1  = GaussianModel(prefix='g1_')
		pars.update(gauss1.make_params())
		
		pars['g1_center'].set(center[0], min=1.6, max=2.0)
		pars['g1_sigma'].set(0.08, min=0.01, max=0.15)
		pars['g1_amplitude'].set(max_val[0], min=0.1)

		gauss2  = GaussianModel(prefix='g2_')
		pars.update(gauss2.make_params())

		pars['g2_center'].set(center[1], min=2.05, max=2.4)
		pars['g2_sigma'].set(0.12, min=0.01, max=0.15)
		pars['g2_amplitude'].set(max_val[1], min=0.1)

		gauss3  = GaussianModel(prefix='g3_')
		pars.update(gauss3.make_params())
		
		pars['g3_center'].set(center[2], min=2.7, max=3.0)
		pars['g3_sigma'].set(0.08, min=0.01, max=0.2)
		pars['g3_amplitude'].set(max_val[2], min=0.1)

		gauss4  = GaussianModel(prefix='g4_')
		pars.update(gauss4.make_params())
		
		pars['g4_center'].set(center[3], min=3.3, max=3.8)
		pars['g4_sigma'].set(0.08, min=0.01, max=0.2)
		pars['g4_amplitude'].set(max_val[3], min=0.01)


		mod = gauss1 + gauss2 + gauss3 + gauss4 + exp_mod

		init = mod.eval(pars, x=x)
		out = mod.fit(y, pars, x=x)
		comps = out.eval_components(x=x)

		area = np.vstack([area,[sample,round(np.trapz(comps['g2_'],dx=1),1)]])

		if '-nograph' in sys.argv:  ###### Plotting of fit
			pass
		else:
			plt.clf()
			fig, ax1 = plt.subplots()

			ax1.plot(volume1, data1, 'g-')
			ax1.set_xlabel('Volume (ml)')
			ax1.set_ylabel('Fluorescence'+' ('+ytitle[0]+')', color='g')
			ax1.grid(b=True, which='major', color='#666666', linestyle='-', alpha=0.2)

			plt.plot(x, out.best_fit, 'r--')
			plt.plot(x, comps['g2_'], 'b-')

			plt.savefig(dir_fit+'/'+sample+'_fit', dpi=200)
			plt.close()

		percent = (progress/number) ##### Progress bar
		hashes = '#' * int(round(percent * bar_length))
		spaces = ' ' * (bar_length - len(hashes))
		sys.stdout.write("\rProgress: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
		sys.stdout.flush()
		progress +=1

##### End of routine

np.savetxt(dir_fit+'/'+'area.txt',area,fmt='%s',delimiter=' ', header='Peak area')

print('\n\nTasks completed within %s seconds!' % round((timeit.default_timer() - start_time),1))
print('\n\nDone!\n')
