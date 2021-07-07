import arcpy
import os
import traceback
import sys

from NSRN_Checks import Var
from NSRN_Checks import logger
try:
    logfile = logger(__name__)
    arcpy.env.workspace = Var.ws
    arcpy.env.scratchworkspace = Var.sws
    arcpy.env.overwriteOutput = True
    arcpy.env.XYTolerance = Var.XYTolerance

    arcpy.MakeFeatureLayer_management(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'SmallSegments_lyr', '"Shape_Length" < 2.5 AND "SEGID" > 0')
    cntchk = int(arcpy.GetCount_management('SmallSegments_lyr')[0])
    if cntchk == False:
        logfile.error('No Road Segments Are Smaller than 2.5 Metres\n')
    else:
        logfile.info('SmallSegments_lyr Created')
        arcpy.CalculateField_management('SmallSegments_lyr',  'ErrorType',  "'Investigate'", 'PYTHON')
        logfile.info('Small Segments Have Been Identified - Select Investigate In The ErrorType Field\n')

    arcpy.Compact_management(Var.gdb)
    logfile.info(str(Var.day) + ' DB Compacted\n')

except:
    logfile.critical('Something Went Wrong...')
    logfile.critical(traceback.format_exc())
    sys.exit()

del arcpy
