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


    def lrscheck(distance):
        arcpy.MakeTableView_management(Var.gdb + os.sep + 'LRS', 'LTV', 'ErrorType IS NULL')
        if int(arcpy.GetCount_management('LTV').getOutput(0)) > 0:
            with arcpy.da.SearchCursor('LTV', ['ROADSEGID', 'IDS', 'START_DIST', 'STOP_DIST']) as cur:
                for row in cur:
                    print('### Processing ###')
                    print('       SEGID: ' + str(row[0]))
                    print('         IDS: ' + str(row[1]))
                    print('  Start Dist: ' + str(row[2]))
                    print('   Stop Dist: ' + str(row[3]))
                    print('  Difference: ' + str(abs(row[3]) - abs(row[2])))
                    if abs(row[3]) - abs(row[2]) <= distance:
                        print(' ERROR - LRS RECORD NEEDS TO BE EXAMINED')
                        print(' SEGMENT IS LESS THAN ' + str(distance) + ' METRES')
                        with arcpy.da.UpdateCursor('LTV', ['ErrorType'], 'ROADSEGID = ' + str(int(row[0]))) as ucur:
                            for urow in ucur:
                                urow[0] = 'Possible Error'
                                ucur.updateRow(urow)
                    print('###   Done   ###\n')
        else:
            print('There Are No LRS Segments Needing Work\n')
        arcpy.Delete_management('LTV')
        return


    def cmpt ():
        arcpy.Compact_management(Var.gdb)
        print(str(Var.day) + ' DB Compacted\n')
        return

    lrscheck(2.5)
    print('Sub 2.5 Metre Check Complete')
    cmpt()
    # lrscheck(5)
    # print('Sub 5 Metre Check Complete'
    # cmpt()

except:
    print('Something Went Wrong...')
    print(traceback.format_exc())
    sys.exit()

del arcpy
