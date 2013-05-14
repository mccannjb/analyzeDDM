import numpy as np
import re
import sys

### Map Masking functions ###
def readMap(mapFile,fileRows,fileCols):
        mask=np.array(np.genfromtxt(mapFile,dtype=int),dtype=bool)
        if mask.shape[0]==fileRows and mask.shape[1]==fileCols:
                return mask
        else:
                print "{} != {} or {} != {}".format(mask.shape[0],fileRows,mask.shape[1],fileCols)
                sys.exit("Map file grid dimensions != Sensitivity grid dimensions")

def indexPts(mask):
        grdX,grdY=np.nonzero(mask)      # Creates an array of X-indices and an array of Y-indices 
        return grdX,grdY                # where X,Y is the location in [mask] of a non-zero value

### Arithmatic functions ###
def avgSens(sens,grdX,grdY):
	xmin = grdX.min() 
	xmax = grdX.max()+1
	ymin = grdY.min()
	ymax = grdY.max()+1
	mean = np.mean(sens[ymin:ymax,xmin:xmax])
	return mean
#        total=0
#        for idx,x in enumerate(grdX):
#  		total+=sens[grdY[idx],x]
#        return total/float(len(grdX))

### Parsing functions ###
def getRegion(key):
        p='(\d+)E(\d{2})(\d{2})(\w+)'
        r=re.match(p,str(key))
        if r:
                return r.group(3)
        else:
                sys.exit('Error parsing key name: {}'.format(key))

### Rename sens variable if iterating through multiple files ###
def renameSens(sens_key,group):
        if group==1:		## If the group number is 1, no modification necessary
                return sens_key	
        if group>1:		## If the group number is >1, need to modify the sens name
                newRegion=int(getRegion(sens_key))+11*(group-1)
                return "05E01{0:02d}NOX".format(newRegion)
