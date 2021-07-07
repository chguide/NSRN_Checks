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


    def flyr(fc, lyr, query=None):
        arcpy.MakeFeatureLayer_management(Var.gdb + os.sep + 'Data' + os.sep + fc, lyr, query)
        print(lyr + ' Created')
        return


    def sbl(inlyr, sel, sellyr, query):
        arcpy.SelectLayerByLocation_management(inlyr, sel, sellyr)
        chk = int(arcpy.GetCount_management(inlyr)[0])
        if chk == 0:
            print('No ' + sellyr + ' Points Match Any Topology Error Points')
        else:
            arcpy.CalculateField_management(inlyr, 'ErrorType', query, 'PYTHON')
            arcpy.SelectLayerByAttribute_management(inlyr, 'CLEAR_SELECTION')
            arcpy.SelectLayerByAttribute_management(sellyr, 'CLEAR_SELECTION')
            print(sellyr + ' Points Have Been Identified')
        return


    def cmpt ():
        arcpy.Compact_management(Var.gdb)
        print(str(Var.day) + ' DB Compacted\n')
        return


    def validbreaks(field, calculate):
        # global errorpts_lyr, roads_lyr
        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'NEW_SELECTION', "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
        with arcpy.da.SearchCursor('errorpts_lyr', ['OID@', 'ErrorType'], 'ErrorType IS NULL') as scur:
            for row in scur:
                print('###   Starting Error Point   ###')
                print('OID: ' + str(row[0]))
                arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'NEW_SELECTION', 'OID = ' + str(row[0]))
                arcpy.SelectLayerByLocation_management('roads_lyr', 'INTERSECT', 'errorpts_lyr')
                with arcpy.da.SearchCursor('roads_lyr',
                                           [field]) as roadcur:
                    chklist = []
                    for rdrow in roadcur:
                        rd1 = rdrow[0]
                        chklist.append(str(rd1))
                        print(field + ": " + str(rd1))
                    if chklist[0] == chklist[1]:
                        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
                        arcpy.SelectLayerByAttribute_management('roads_lyr', 'CLEAR_SELECTION')
                        print('Values match - Possible error')
                        print('###   Finished Error Point   ###\n')
                    else:
                        with arcpy.da.UpdateCursor('errorpts_lyr', ['OID@', 'ErrorType'], "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'") as ucur:
                            for urow in ucur:
                                urow[1] = calculate
                                ucur.updateRow(urow)
                        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
                        arcpy.SelectLayerByAttribute_management('roads_lyr', 'CLEAR_SELECTION')
                        print('Values are different - False error')
                        print('###   Finished Error Point   ###\n')
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
                print('###   Starting Error Point   ###')
                print('OID: ' + str(row[0]))
                arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'NEW_SELECTION', 'OID = ' + str(row[0]))
                arcpy.SelectLayerByLocation_management('roads_lyr', 'INTERSECT', 'errorpts_lyr')
                with arcpy.da.SearchCursor('roads_lyr', [field]) as rdcur:
                    chklist = []
                    for rdrow in rdcur:
                        rd1 = rdrow[0]
                        chklist.append(str(rd1))
                        print(field + ": " + str(rd1))
                    if chklist[0] == val and chklist[1] == val:
                        with arcpy.da.UpdateCursor('errorpts_lyr', ['OID@', 'ErrorType'], "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'") as ucur:
                            for urow in ucur:
                                urow[1] = calculate
                                ucur.updateRow(urow)
                        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
                        arcpy.SelectLayerByAttribute_management('roads_lyr', 'CLEAR_SELECTION')
                        print('Values match - False error')
                        print('###   Finished Error Point   ###\n')
                    else:
                        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
                        arcpy.SelectLayerByAttribute_management('roads_lyr', 'CLEAR_SELECTION')
                        print('Values are different - Possible error')
                        print('###   Finished Error Point   ###\n')
        arcpy.SelectLayerByAttribute_management('errorpts_lyr', 'CLEAR_SELECTION')
        arcpy.SelectLayerByAttribute_management('roads_lyr', 'CLEAR_SELECTION')
        cmpt()
        return

    flyr('Topology_point', 'errorpts_lyr', "RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
    flyr('GSA', 'gsa_lyr')
    flyr('BlockedPassages', 'blkpsg_lyr')
    flyr('NSRN', 'roads_lyr')
    print('')

    # sbl('errorpts_lyr', 'ARE_IDENTICAL_TO', 'blkpsg_lyr', "'Blocked Passage'")
    sbl('errorpts_lyr', 'BOUNDARY_TOUCHES', 'gsa_lyr', "'Community Boundary'")
    print('Initial Classifications Are Done\n')

    arcpy.AddIndex_management('errorpts_lyr', ['OriginObjectID', 'DestinationObjectID'], 'error_points')
    print('errorpts_lyr Indexes Added\n')

    cmpt()

    validbreaks('ROADCLASS', 'Road Class Change')
    print('Matching Road Class Errors Classified')
    cmpt()
    validbreaks('OWNER', 'Owner Change')
    print('Matching Owner Errors Classified')
    cmpt()
    validbreaks('MUN_ID', 'MUNID Change')
    print('Matching MUNID Errors Classified')
    cmpt()
    validbreaks('STREET', 'Street Name Change')
    print('Matching Street Name Errors Classified')
    cmpt()
    rdmatch('ROADCLASS', 'DW', 'Dry Weather')
    print('Dry Weather Roads Classified')
    cmpt()
    rdmatch('ROADCLASS', 'WA', 'Water Access')
    print('Water Access Roads Classified')
    cmpt()

    flyr('Topology_point', 'viewpoints_lyr', "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
    arcpy.CalculateField_management('viewpoints_lyr', 'ErrorType', "'Investigate'", 'PYTHON')
    print('Points To Exmaine Have Been Identified - Select Investigate In The ErrorType Field\n')

    cmpt()

except:
    print('Something Went Wrong...')
    print(traceback.format_exc())
    sys.exit()

del arcpy

