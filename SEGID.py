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


    def cmpt ():
        arcpy.Compact_management(Var.gdb)
        logfile.info(str(Var.day) + ' DB Compacted\n')
        return

    flyr(Var.gdb + os.sep + 'Data' + os.sep + 'Junctions', 'juncs_1', 'JUNCTYPE = 1')
    flyr(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'dw_lyr', "ROADCLASS LIKE 'DW'")
    flyr(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'tmp_roads', "ROADCLASS NOT LIKE 'DW'")
    logfile.info('')

    arcpy.SelectLayerByLocation_management('juncs_1', 'INTERSECT', 'dw_lyr')
    logfile.info('Selecting Intersections That Touch DryWeather Roads')
    arcpy.SelectLayerByLocation_management('juncs_1', 'INTERSECT', 'tmp_roads', selection_type='REMOVE_FROM_SELECTION')
    logfile.info('Removing Intersections That Touch Non DryWeather Roads')
    arcpy.CalculateField_management('juncs_1', 'ErrorType', "'SEGID 0'", 'PYTHON')
    logfile.info('Setting The Remaining Junctions To SEGID = 0\n')

    flyr(Var.gdb + os.sep + 'Data' + os.sep + 'Junctions', 'juncs_1_null', "ErrorType IS NULL AND JUNCTYPE = 1")
    flyr(Var.sws + os.sep + 'NSRNDissolved', 'diss_roads')
    logfile.info('')

    cmpt()

    totalval = int(arcpy.GetCount_management('juncs_1_null').getOutput(0))
    if totalval > 0:
        arcpy.SelectLayerByAttribute_management('juncs_1_null', 'CLEAR_SELECTION')
        with arcpy.da.SearchCursor('juncs_1_null', ["JUNCTIONID", "SHAPE@"]) as scur:
            for srow in scur:
                logfile.info('###   Starting Junction   ###')
                logfile.info("JunctionID: " + str(srow[0]))
                for pnt in srow[1]:
                    jxy = '{}, {}'.format(pnt.x, pnt.y)
                    logfile.info("                  " + jxy)
                arcpy.SelectLayerByAttribute_management('juncs_1_null', 'NEW_SELECTION', "JUNCTIONID = " + str(srow[0]))
                arcpy.SelectLayerByLocation_management('diss_roads', 'INTERSECT', 'juncs_1_null', selection_type='NEW_SELECTION')
                selchk = int(arcpy.GetCount_management('diss_roads').getOutput(0))
                if selchk > 0:
                    with arcpy.da.SearchCursor('diss_roads', ['SEGID', 'SHAPE@']) as rdcur:
                        chklist = []
                        for rdrow in rdcur:
                            logfile.info("SEGID: " + str(rdrow[0]))
                            startpt = rdrow[1].firstPoint
                            endpt = rdrow[1].lastPoint
                            spnt = '{}, {}'.format(startpt.X, startpt.Y)
                            epnt = '{}, {}'.format(endpt.X, endpt.Y)
                            rdxy = spnt, epnt
                            chklist.append(rdxy)
                            logfile.info("       Start Point: " + spnt)
                            logfile.info("         End Point: " + epnt)
                    matching = [s for s in chklist if jxy in s]
                    if len(chklist) > len(matching):
                        arcpy.SelectLayerByAttribute_management('juncs_1_null', 'NEW_SELECTION', "JUNCTIONID = " + str(srow[0]))
                        arcpy.SelectLayerByLocation_management('dw_lyr', 'INTERSECT', 'juncs_1_null', selection_type='NEW_SELECTION')
                        dw_chk = int(arcpy.GetCount_management('dw_lyr').getOutput(0))
                        if dw_chk == 1:
                            logfile.info('Dry Weather Intersection')
                            with arcpy.da.UpdateCursor('juncs_1_null', ['ErrorType']) as DWcur:
                                for DWrow in DWcur:
                                    DWrow[0] = 'DW Intersection'
                                    DWcur.updateRow(DWrow)
                        else:
                            logfile.info('Possible Error')
                            with arcpy.da.UpdateCursor('juncs_1_null', ['ErrorType']) as ucur:
                                for urow in ucur:
                                    urow[0] = 'Investigate'
                                    ucur.updateRow(urow)
                else:
                    logfile.error('No road selected')
                logfile.info('###   Finished Point   ###\n')
                arcpy.SelectLayerByAttribute_management('juncs_1_null', 'CLEAR_SELECTION')
                arcpy.SelectLayerByAttribute_management('diss_roads', 'CLEAR_SELECTION')
    else:
        logfile.info('There Are No Junctions Needing Processing\n')

    cmpt()

except:
    logfile.critical('Something Went Wrong...')
    logfile.critical(traceback.format_exc())
    sys.exit()

del arcpy
