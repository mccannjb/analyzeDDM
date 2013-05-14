##
##	analyzeDDM
##
##	Author: James McCann (mccannjb (at) gmail (dot) com)
##      Written 05-2013
##
##	Usage: analyzeDDM.py -m <mapfile> -d <day of interest> -s <start hour> [-a (8 hour avg, default)] -i <inputfile>

from PseudoNetCDF.camxfiles.Memmaps import uamiv
from collections import defaultdict
from AnDDM import *
import numpy as np
import sys, getopt
import csv

argv=sys.argv[1:]

inputdir=''
starthour=0
mapfile=''
doi=0
hrrange=8
groups=0
try:
	opts, args = getopt.getopt(argv,"hi:m:d:s:g:a:",["ifiledir=","mapfile=","day=","starthr=","groups="])
except getopt.GetoptError:
	print 'analyzeDDM.py -i <inputfiledir> -m <mapfile> -d <day of interest> -s <start hour> -g <groups> [-a <hours> (8 hour avg, default)]'
	sys.exit(2)
for opt,arg in opts:
	if opt == '-h':
		print 'analyzeDDM.py -i <inputfiledir> -m <mapfile> -d <day of interest> -s <start hour> -g <groups> [-a <hours> (8 hour avg, default)]'
		sys.exit()
	elif opt in ("-i","--ifile"):
		inputdir = arg
	elif opt in ("-m","--mapfile"):
		mapfile = arg
	elif opt in ("-d","--day"):
		try:
			doi = int(arg)
		except ValueError:
			print 'ERROR: day of interest argument must be an integer (eg. 215)'
			sys.exit()
	elif opt in ("-s","--starthr"):
		try:
			starthour = int(arg)
		except ValueError:
			print 'ERROR: starting hour argument must be an integer (eg. 15)'
			sys.exit()
	elif opt == '-a':
		try:
			range = int(arg)
		except ValueError:
			print 'WARNING: averaging hours argument must be an integer (eg. 8), defaulting to 8 hours'
			hrrange = 8
	elif opt in ("-g","--groups"):
		try:
			groups = int(arg)
		except ValueError:
			print 'ERROR: group number argument must be an integer (eg. 8)'
			sys.exit()

print 'Input file directory: {}'.format(inputdir)
print 'Map file: {}'.format(mapfile)
print 'Day of interest: {}'.format(doi)
print 'Starting hour: {} UTC'.format(starthour)
print 'Number of groups: {}'.format(groups)
print 'Averaging hour range: {}'.format(hrrange)

### Set Variables ###
t_rows=240		# These values are the total rows and columns
t_cols=279		# for the 12EUS1 domain, edit only if necessary

endhour=starthour+hrrange

cases = ['NICK_12HR']
species = "05"		# This is the modeled species number of
			# ozone for the simulation.
#####################

# Generate list of group numbers
grps=[i+1 for i in range(groups)]

# Get indices of map
grdXs,grdYs=indexPts(readMap(mapfile,t_rows,t_cols))

# 
allCases={}
for case in cases:
	spatialAvg={}
	for grp in grps:
		filename="{0}-{1:02d}.2005{2}.ddm.grd01".format(case,grp,doi)
		filecall="{0}/{1}/GRP{2:02d}/{3}".format(inputdir,case,grp,filename)
		ddm=uamiv(filecall)
		for key in ddm.variables.keys():
			if key.startswith("{}E".format(species)):
				newKey=renameSens(key,grp)
				srcPt=getRegion(newKey)
				if getRegion(key)=='01':
					print "Skipping group {}".format(srcPt)
				else:
					sens=ddm.variables[key]
					spatialAvg[newKey]=[avgSens(sens[hr,0],grdXs,grdYs) for hr in range(24)]
	allCases[case]=spatialAvg
for akey in sorted(allCases.iterkeys()):
	output=open('{}_hrs{}-{}_DDMavg.out'.format(akey,starthour,endhour),'w')
	headers="Case,Sensitivity,"+','.join(['Hour {0:02d}'.format(hr) for hr in range(24)])+"\n"
	output.write(headers)
	for key in sorted(allCases[akey].iterkeys()):
		wstring = ",".join(['{0:10.3E}'.format(allCases[akey][key][hr]) for hr in range(starthour,endhour+1)])
		output.write("{},{},{}\n".format(akey,key,wstring))
	output.close()
	
