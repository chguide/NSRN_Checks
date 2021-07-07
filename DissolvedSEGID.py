import arcpy
import os
import traceback
import sys

from NSRN_Checks import Var
from NSRN_Checks import logger
try:
    logfile = logger(__name__)
    arcpy.env.workspace = Var.ws
    arcpy.env.scratchWorkspace = Var.sws
    arcpy.env.overwriteOutput = True
    arcpy.env.XYTolerance = Var.XYTolerance


    def flyr(fc, lyr, query=None):
        arcpy.MakeFeatureLayer_management(fc, lyr, query)
        logfile.info(lyr + ' Created')
        return


    def addindex(fc, fields, name):
        arcpy.AddIndex_management(fc, fields, name)
        logfile.info(fc.rsplit(os.sep, 1)[1] + ' Indexes Added')
        return


    flyr(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'SEGID0_lyr', '"SEGID" <> 0')
    logfile.info('')

    arcpy.Dissolve_management('SEGID0_lyr', Var.sws + os.sep + 'NSRNDissolved', "SEGID", multi_part="SINGLE_PART")
    logfile.info('roads_lyr Dissolved\n')

    addindex(Var.sws + os.sep + 'NSRNDissolved', ['SEGID'], 'NSRN_Dissolved')
    logfile.info('')

    arcpy.Statistics_analysis(Var.sws + os.sep + 'NSRNDissolved', Var.sws + os.sep + 'NSRNDissolvedStats', "SEGID COUNT", "SEGID")
    logfile.info('roads_lyr Statistics Created\n')

    addindex(Var.sws + os.sep + 'NSRNDissolvedStats', ['SEGID'], 'NSRNDissolvedStats')
    logfile.info('')

    flyr(Var.sws + os.sep + 'NSRNDissolved', 'roads_diss')
    logfile.info('')

    arcpy.AddJoin_management('roads_diss', 'SEGID', Var.sws + os.sep + 'NSRNDissolvedStats', 'SEGID')
    logfile.info('Statistics Joined to Roads\n')

    arcpy.SelectLayerByAttribute_management('roads_diss', 'NEW_SELECTION', 'FREQUENCY > 1')
    logfile.info('Checking For Multiple SEGIDs')

    freqchk = int(arcpy.GetCount_management('roads_diss')[0])
    if freqchk == 0:
        logfile.warning('No SEGIDs Have More Than One Dissolved Segment\n')
    else:
        logfile.info('There Are SEGIDs To Examine\n')
        arcpy.TableToTable_conversion('roads_diss', Var.gdb, 'MultipleSEGID')
        arcpy.AddField_management(Var.gdb + os.sep + 'MultipleSEGID', 'ErrorType', 'TEXT')
        arcpy.CalculateField_management(Var.gdb + os.sep + 'MultipleSEGID', 'ErrorType', "'Investigate'", 'PYTHON')

    arcpy.Compact_management(Var.gdb)
    logfile.info(str(Var.day) + ' DB Compacted\n')

except:
    logfile.critical('Something Went Wrong...')
    logfile.critical(traceback.format_exc())
    sys.exit()

del arcpy
