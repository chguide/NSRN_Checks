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


    def selup(dataset, value):
        arcpy.MakeFeatureLayer_management(comparedb + os.sep + 'Data' + os.sep + dataset, 'compare', 'ErrorType LIKE ' + "'" + value + "'")
        query_chk = int(arcpy.GetCount_management('compare')[0])
        if query_chk == 0:
            logfile.warning('There Are No ' + value + ' Compare Points - Moving On\n')
        else:
            arcpy.MakeFeatureLayer_management(currentdb + os.sep + 'Data' + os.sep + dataset, 'current')
            arcpy.SelectLayerByLocation_management('current', 'INTERSECT', 'compare')
            sel_chk = int(arcpy.GetCount_management('current')[0])
            if sel_chk == 0:
                logfile.warning('There Are No ' + value + ' Current Points - Moving On\n')
            else:
                arcpy.CalculateField_management('current', 'ErrorType', "'" + value + "'", 'PYTHON')
                logfile.info(str(query_chk) + ' ' + value + ' Records Processed\n')
        arcpy.Delete_management('current')
        arcpy.Delete_management('compare')
        return

    dir_list = next(os.walk(Var.ws))[1]
    numlist = []
    print(dir_list)
    for item in dir_list:
        if item == 'Scratch.gdb':
            logfile.info('Scratch Workspace Found - Skipping')
        elif item == 'PseudoNodes.gdb':
            logfile.info('Former Pesudo Nodes Database Found - Skipping')
        else:
            item = item[:-4]
            numlist.append(int(item))
    numlist.sort(reverse=True)

    if len(numlist) < 2:
        logfile.error('Only One GDB - Processing Must Be Done Manually\n')

    else:
        currentdb = Var.ws + os.sep + str(numlist[0]) + '.gdb'
        comparedb = Var.ws + os.sep + str(numlist[1]) + '.gdb'
        curtp_chk = arcpy.Exists(currentdb + os.sep + 'Data' + os.sep + 'Topology_point')
        if curtp_chk is False:
            logfile.warning(str(numlist[0]) + '.gdb (The Current DB) Does Not Contain Topology Points - Comparison & Updates Will Be Skipped')
        else:
            selup('Topology_point', 'Anomaly')
            selup('Topology_point', 'Blocked Passage')
            selup('Topology_point', 'Cul-de-sac')
            selup('Topology_point', 'Fix')
            selup('Topology_point', 'GSA Split')
            selup('Topology_point', 'Highway Exit')
            selup('Topology_point', 'Traffic Direction')
            selup('Topology_point', 'Under Investigation')
            selup('Topology_point', 'Valid')

            selup('Junctions', 'Dry Weather')
            selup('Junctions', 'SEGID 0')

            arcpy.Compact_management(Var.gdb)
            logfile.info(str(Var.day) + ' DB Compacted\n')

except:
    logfile.critical('Something Went Wrong...')
    logfile.critical(traceback.format_exc())
    sys.exit()

del arcpy
