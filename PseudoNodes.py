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
        arcpy.MakeFeatureLayer_management(Var.gdb + os.sep + 'Data' + os.sep + fc, lyr, query)
        logfile.info(lyr + ' Created')
        return


    def sbl(inlyr, sel, sellyr, query):
        arcpy.SelectLayerByLocation_management(inlyr, sel, sellyr)
        chk = int(arcpy.GetCount_management(inlyr)[0])
        if chk == 0:
            logfile.warning('No ' + sellyr + ' Points Match Any Topology Error Points')
        else:
            arcpy.CalculateField_management(inlyr, 'ErrorType', query, 'PYTHON')
            arcpy.SelectLayerByAttribute_management(inlyr, 'CLEAR_SELECTION')
            arcpy.SelectLayerByAttribute_management(sellyr, 'CLEAR_SELECTION')
            logfile.info(sellyr + ' Points Have Been Identified')
        return


    def cmpt ():
        arcpy.Compact_management(Var.gdb)
        logfile.info(str(Var.day) + ' DB Compacted\n')
        return


    def validbreaks(field, calculate):
        # global errorpts_lyr, roads_lyr
        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'NEW_SELECTION', "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
        with arcpy.da.SearchCursor('errorpts_lyr', ['OID@', 'ErrorType'], 'ErrorType IS NULL') as scur:
            for row in scur:
                logfile.info('###   Starting Error Point   ###')
                logfile.info('OID: ' + str(row[0]))
                arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'NEW_SELECTION', 'OID = ' + str(row[0]))
                arcpy.SelectLayerByLocation_management('roads_lyr', 'INTERSECT', 'errorpts_lyr')
                with arcpy.da.SearchCursor('roads_lyr', [field]) as roadcur:
                    chklist = []
                    for rdrow in roadcur:
                        rd1 = rdrow[0]
                        chklist.append(str(rd1))
                        logfile.info(field + ": " + str(rd1))
                    if chklist[0] == chklist[1]:
                        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
                        arcpy.SelectLayerByAttribute_management('roads_lyr', 'CLEAR_SELECTION')
                        logfile.info('Values match - Possible error')
                        logfile.info('###   Finished Error Point   ###\n')
                    else:
                        with arcpy.da.UpdateCursor('errorpts_lyr', ['OID@', 'ErrorType'], "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'") as ucur:
                            for urow in ucur:
                                urow[1] = calculate
                                ucur.updateRow(urow)
                        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
                        arcpy.SelectLayerByAttribute_management('roads_lyr', 'CLEAR_SELECTION')
                        logfile.info('Values are different - False error')
                        logfile.info('###   Finished Error Point   ###\n')
        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
        arcpy.SelectLayerByAttribute_management('roads_lyr', 'CLEAR_SELECTION')
        cmpt()
        return


    def rdmatch(field, val, calculate):
        # global errorpts_lyr, roads_lyr
        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'NEW_SELECTION', "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
        with arcpy.da.SearchCursor('errorpts_lyr', ['OID@', 'ErrorType'], 'ErrorType IS NULL') as scur:
            for row in scur:
                logfile.info('###   Starting Error Point   ###')
                logfile.info('OID: ' + str(row[0]))
                arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'NEW_SELECTION', 'OID = ' + str(row[0]))
                arcpy.SelectLayerByLocation_management('roads_lyr', 'INTERSECT', 'errorpts_lyr')
                with arcpy.da.SearchCursor('roads_lyr', [field]) as rdcur:
                    chklist = []
                    for rdrow in rdcur:
                        rd1 = rdrow[0]
                        chklist.append(str(rd1))
                        logfile.info(field + ": " + str(rd1))
                    if chklist[0] == val and chklist[1] == val:
                        with arcpy.da.UpdateCursor('errorpts_lyr', ['OID@', 'ErrorType'], "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'") as ucur:
                            for urow in ucur:
                                urow[1] = calculate
                                ucur.updateRow(urow)
                        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
                        arcpy.SelectLayerByAttribute_management('roads_lyr', 'CLEAR_SELECTION')
                        logfile.info('Values match - False error')
                        logfile.info('###   Finished Error Point   ###\n')
                    else:
                        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
                        arcpy.SelectLayerByAttribute_management('roads_lyr', 'CLEAR_SELECTION')
                        logfile.info('Values are different - Possible error')
                        logfile.info('###   Finished Error Point   ###\n')
        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
        arcpy.SelectLayerByAttribute_management('roads_lyr', 'CLEAR_SELECTION')
        cmpt()
        return

    flyr('Topology_point', 'errorpts_lyr', "RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
    flyr('GSA', 'gsa_lyr')
    flyr('BlockedPassages', 'blkpsg_lyr')
    flyr('NSRN', 'roads_lyr', 'IDS > 0')
    logfile.info('')

    sbl('errorpts_lyr', 'ARE_IDENTICAL_TO', 'blkpsg_lyr', "'Blocked Passage'")
    sbl('errorpts_lyr', 'BOUNDARY_TOUCHES', 'gsa_lyr', "'Community Boundary'")
    logfile.info('Initial Classifications Are Done\n')

    arcpy.AddIndex_management('errorpts_lyr', ['OriginObjectID', 'DestinationObjectID'], 'error_points')
    logfile.info('errorpts_lyr Indexes Added\n')

    cmpt()

    validbreaks('ROADCLASS', 'Road Class Change')
    logfile.info('Matching Road Class Errors Classified')
    cmpt()
    validbreaks('OWNER', 'Owner Change')
    logfile.info('Matching Owner Errors Classified')
    cmpt()
    validbreaks('MUN_ID', 'MUNID Change')
    logfile.info('Matching MUNID Errors Classified')
    cmpt()
    validbreaks('STREET', 'Street Name Change')
    logfile.info('Matching Street Name Errors Classified')
    cmpt()
    rdmatch('ROADCLASS', 'DW', 'Dry Weather')
    logfile.info('Dry Weather Roads Classified')
    cmpt()
    rdmatch('ROADCLASS', 'WA', 'Water Access')
    logfile.info('Water Access Roads Classified')
    cmpt()

    flyr('Topology_point', 'viewpoints_lyr', "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
    arcpy.CalculateField_management('viewpoints_lyr', 'ErrorType', "'Investigate'", 'PYTHON')
    logfile.info('Points To Exmaine Have Been Identified - Select Investigate In The ErrorType Field\n')

    cmpt()

except:
    logfile.critical('Something Went Wrong...')
    logfile.critical(traceback.format_exc())
    sys.exit()

del arcpy

