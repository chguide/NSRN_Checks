import arcpy
import os
import traceback
import sys

from NSRN_Checks import Var

try:
    arcpy.env.workspace = Var.ws
    arcpy.env.scratchworkspace = Var.sws
    arcpy.env.overwriteOutput = True
    arcpy.env.XYTolerance = Var.XYTolerance

    arcpy.MakeFeatureLayer_management(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'SmallSegments_lyr', '"Shape_Length" < 5 AND "SEGID" > 0')
    cntchk = int(arcpy.GetCount_management('SmallSegments_lyr')[0])
    if cntchk == False:
        print('No Road Segments Are Smaller than 5 Metres\n')
    else:
        print('SmallSegments_lyr Created')
        arcpy.CalculateField_management('SmallSegments_lyr',  'ErrorType',  "'Investigate'", 'PYTHON')
        print('Small Segments Have Been Identified - Select Investigate In The ErrorType Field\n')

    arcpy.Compact_management(Var.gdb)
    print(str(Var.day) + ' DB Compacted\n')

except:
    print('Something Went Wrong...')
    print(traceback.format_exc())
    sys.exit()

del arcpy
