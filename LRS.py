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


    def lrscheck(distance):
        arcpy.MakeTableView_management(Var.gdb + os.sep + 'LRS', 'LTV', 'IDS > 0')
        if int(arcpy.GetCount_management('LTV').getOutput(0)) > 0:
            with arcpy.da.SearchCursor('LTV', ['ROADSEGID', 'IDS', 'START_DIST', 'STOP_DIST']) as cur:
                for row in cur:
                    logfile.info('### Processing ###')
                    logfile.info('       SEGID: ' + str(row[0]))
                    logfile.info('         IDS: ' + str(row[1]))
                    logfile.info('  Start Dist: ' + str(row[2]))
                    logfile.info('   Stop Dist: ' + str(row[3]))
                    logfile.info('  Difference: ' + str(abs(row[3]) - abs(row[2])))
                    if abs(row[3]) - abs(row[2]) <= distance:
                        logfile.info(' ERROR - LRS RECORD NEEDS TO BE EXAMINED')
                        logfile.info(' SEGMENT IS LESS THAN ' + str(distance) + ' METRES')
                        with arcpy.da.UpdateCursor('LTV', ['ErrorType'], 'ROADSEGID = ' + str(int(row[0]))) as ucur:
                            for urow in ucur:
                                urow[0] = 'Investigate'
                                ucur.updateRow(urow)
                    logfile.info('###   Done   ###\n')
        else:
            logfile.warning('There Are No LRS Segments Needing Work\n')
        arcpy.Delete_management('LTV')
        return


    def cmpt ():
        arcpy.Compact_management(Var.gdb)
        logfile.info(str(Var.day) + ' DB Compacted\n')
        return

    lrscheck(2.5)
    logfile.info('Sub 2.5 Metre Check Complete')
    cmpt()
    # lrscheck(5)
    # logfile.info('Sub 5 Metre Check Complete')
    # cmpt()

    # arcpy.MakeTableView_management(Var.gdb + os.sep + 'LRS', 'LTV_chk', 'ErrorType IS NOT NULL')
    # ltv_cnt = int(arcpy.GetCount_management('LTV_chk')[0])
    # if ltv_cnt == 0:
    #     logfile.info('')
    # else:
    #     arcpy.DeleteRows('LTV_chk')

except:
    logfile.critical('Something Went Wrong...')
    logfile.critical(traceback.format_exc())
    sys.exit()

del arcpy
