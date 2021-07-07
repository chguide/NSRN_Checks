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


    def flyr(fc, lyr, query=None):
        arcpy.MakeFeatureLayer_management(fc, lyr, query)
        logfile.info(lyr + ' Created')
        return


    def sbl(inlyr, sel, sellyr, query):
        arcpy.SelectLayerByLocation_management(inlyr, sel, sellyr)
        chk = int(arcpy.GetCount_management(inlyr)[0])
        if chk == 0:
            logfile.error('No ' + sellyr + ' Points Match Any Topology Error Points')
        else:
            arcpy.CalculateField_management(inlyr, 'ErrorType', query, 'PYTHON')
            arcpy.SelectLayerByAttribute_management(inlyr, 'CLEAR_SELECTION')
            arcpy.SelectLayerByAttribute_management(sellyr, 'CLEAR_SELECTION')
            logfile.info(sellyr + ' Points Have Been Identified')
        return

    flyr(Var.gdb + os.sep + 'Data' + os.sep + 'Topology_point', 'errorpts_lyr_dangles', "RuleDescription LIKE 'Must Not Have Dangles'")
    flyr(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'roads_lyr', 'IDS > 0')
    flyr(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'roads_lyr_DW', "ROADCLASS = 'DW'")
    flyr(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'roads_lyr_WA', "ROADCLASS = 'WA'")
    logfile.info('')

    logfile.info('Selecting Roads - Dry Weather')
    sbl('errorpts_lyr_dangles', 'INTERSECT', 'roads_lyr_DW', "'Dry Weather'")
    logfile.info('Selecting Roads - Water Access')
    sbl('errorpts_lyr_dangles', 'INTERSECT', 'roads_lyr_WA', "'Water Access'")
    logfile.info('')

    flyr(Var.gdb + os.sep + 'Data' + os.sep + 'Topology_point', 'errorpts_lyr_dangles_NULL', "RuleDescription LIKE 'Must Not Have Dangles' AND ErrorType IS NULL")
    logfile.info('')

    epdn_chk = int(arcpy.GetCount_management('errorpts_lyr_dangles_NULL')[0])
    if epdn_chk == 0:
        logfile.error('No Dangle Error Points Can Be Processed - None Are NULL')
    else:
        logfile.info('Buffering Possible Errors')
        arcpy.Buffer_analysis('errorpts_lyr_dangles_NULL',  Var.sws + os. sep + 'buffer', '5 Meters')
        
        flyr(Var.sws + os. sep + 'buffer', 'buff_pts')
        
        arcpy.SelectLayerByLocation_management('roads_lyr', 'INTERSECT', 'buff_pts')
        buf_chk = int(arcpy.GetCount_management('roads_lyr')[0])
        if buf_chk == 0:
            logfile.error('No Roads Touch Any Buffers')
        else:
            logfile.info('Identifying Errors')
            arcpy.SelectLayerByLocation_management('roads_lyr', 'INTERSECT', 'errorpts_lyr_dangles_NULL', selection_type="REMOVE_FROM_SELECTION")
            rd_chk = int(arcpy.GetCount_management('roads_lyr')[0])
            if rd_chk == 0:
                logfile.error("No Roads Touch Dangle Error Points")
            else:
                arcpy.SelectLayerByLocation_management('buff_pts', 'INTERSECT', 'roads_lyr', selection_type='NEW_SELECTION')
                rd_buf_chk = int(arcpy.GetCount_management('roads_lyr')[0])
                if rd_buf_chk == 0:
                    logfile.error("No buffers Intersect The Current Road Selection")
                else:
                    arcpy.SelectLayerByLocation_management('errorpts_lyr_dangles_NULL', 'WITHIN', 'buff_pts', selection_type='NEW_SELECTION')
                    arcpy.CalculateField_management('errorpts_lyr_dangles_NULL', 'ErrorType', "'Investigate'", 'PYTHON')
                    logfile.info('Points To Exmaine Have Been Identified - Select Investigate In The ErrorType Field')
    logfile.info('')
                    
    arcpy.Compact_management(Var.gdb)
    logfile.info(str(Var.day) + ' DB Compacted\n')

except:
    logfile.critical('Something Went Wrong...')
    logfile.critical(traceback.format_exc())
    sys.exit()

del arcpy
