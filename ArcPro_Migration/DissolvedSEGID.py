import arcpy
import os
import traceback
import sys

from NSRN_Checks import Var

try:
    arcpy.env.workspace = Var.ws
    arcpy.env.scratchWorkspace = Var.sws
    arcpy.env.overwriteOutput = True
    arcpy.env.XYTolerance = Var.XYTolerance


    def flyr(fc, lyr, query=None):
        arcpy.MakeFeatureLayer_management(fc, lyr, query)
        print(lyr + ' Created')
        return


    def addindex(fc, fields, name):
        arcpy.AddIndex_management(fc, fields, name)
        print(fc.rsplit(os.sep, 1)[1] + ' Indexes Added')
        return


    flyr(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'SEGID0_lyr', '"SEGID" <> 0')
    print('')

    arcpy.Dissolve_management('SEGID0_lyr', Var.sws + os.sep + 'NSRNDissolved', "SEGID", multi_part="SINGLE_PART")
    print('roads_lyr Dissolved\n')

    addindex(Var.sws + os.sep + 'NSRNDissolved', ['SEGID'], 'NSRN_Dissolved')
    print('')

    arcpy.Statistics_analysis(Var.sws + os.sep + 'NSRNDissolved', Var.sws + os.sep + 'NSRNDissolvedStats', "SEGID COUNT", "SEGID")
    print('roads_lyr Statistics Created\n')

    addindex(Var.sws + os.sep + 'NSRNDissolvedStats', ['SEGID'], 'NSRNDissolvedStats')
    print('')

    flyr(Var.sws + os.sep + 'NSRNDissolved', 'roads_diss')
    print('')

    arcpy.AddJoin_management('roads_diss', 'SEGID', Var.sws + os.sep + 'NSRNDissolvedStats', 'SEGID')
    print('Statistics Joined to Roads\n')

    arcpy.SelectLayerByAttribute_management('roads_diss', 'NEW_SELECTION', 'FREQUENCY > 1')
    print('Checking For Multiple SEGIDs')

    freqchk = int(arcpy.GetCount_management('roads_diss')[0])
    if freqchk == 0:
        print('No SEGIDs Have More Than One Dissolved Segment\n')
    else:
        print('There Are SEGIDs To Examine\n')
        arcpy.TableToTable_conversion('roads_diss', Var.gdb, 'MultipleSEGID')

    arcpy.Compact_management(Var.gdb)
    print(str(Var.day) + ' DB Compacted\n')

except:
    print('Something Went Wrong...')
    print(traceback.format_exc())
    sys.exit()

del arcpy
