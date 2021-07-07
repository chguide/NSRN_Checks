import arcpy, os, sys
from datetime import *
start_time = datetime.now()

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'D:\Work\SEGID_Check\Attempt3\GDB.gdb'
ws = arcpy.env.workspace
junctions = 'junctions_lyr'
roads_lyr = 'roads_lyr'
dw_lyr = 'dw_lyr'
arcpy.MakeFeatureLayer_management(ws + os.sep + 'SEGID_Checks_Junctions_Intersections', junctions, "PointType IS NULL", workspace='in_memory')
arcpy.MakeFeatureLayer_management(ws + os.sep + 'SEGID_Checks_Roads_Dissolve', roads_lyr, workspace='in_memory')
arcpy.MakeFeatureLayer_management(ws + os.sep + 'SEGID_Checks_Roads', dw_lyr, "ROADCLASS LIKE 'DW'", workspace='in_memory')

totalval = int(arcpy.GetCount_management(junctions).getOutput(0))
if totalval > 0:
    arcpy.SelectLayerByAttribute_management(junctions, 'CLEAR_SELECTION')
    arcpy.SetProgressor('step', 'Checking for SEGID errors...', 0, totalval, 1)
    with arcpy.da.SearchCursor(junctions, ["JUNCTIONID", "SHAPE@"]) as scur:
        for srow in scur:
            arcpy.SetProgressorLabel('Loading JunctionID:{0}...'.format(srow[0]))
            arcpy.AddMessage('###   Starting Junction   ###')
            arcpy.AddMessage("JunctionID: " + str(srow[0]))
            for pnt in srow[1]:
                jxy = '{}, {}'.format(pnt.x, pnt.y)
                arcpy.AddMessage("                  " + jxy)
            arcpy.SelectLayerByAttribute_management(junctions, 'NEW_SELECTION', "JUNCTIONID = " + str(srow[0]))
            arcpy.SelectLayerByLocation_management(roads_lyr, 'INTERSECT', junctions, selection_type='NEW_SELECTION')
            selchk = int(arcpy.GetCount_management(roads_lyr).getOutput(0))
            if selchk > 0:
                with arcpy.da.SearchCursor(roads_lyr, ['SEGID', 'SHAPE@']) as rdcur:
                    chklist = []
                    for rdrow in rdcur:
                        arcpy.AddMessage("SEGID: " + str(rdrow[0]))
                        startpt = rdrow[1].firstPoint
                        endpt = rdrow[1].lastPoint
                        spnt = '{}, {}'.format(startpt.X, startpt.Y)
                        epnt = '{}, {}'.format(endpt.X, endpt.Y)
                        rdxy = spnt, epnt
                        chklist.append(rdxy)
                        arcpy.AddMessage("       Start Point: " + spnt)
                        arcpy.AddMessage("         End Point: " + epnt)
                    # print chklist
                matching = [s for s in chklist if jxy in s]
                if len(chklist) > len(matching):
                    arcpy.SelectLayerByAttribute_management(junctions, 'NEW_SELECTION', "JUNCTIONID = " + str(srow[0]))
                    arcpy.SelectLayerByLocation_management(dw_lyr, 'INTERSECT', junctions, selection_type='NEW_SELECTION')
                    dw_chk = int(arcpy.GetCount_management(dw_lyr).getOutput(0))
                    # print dw_chk
                    if dw_chk == 1:
                        print 'Dry Weather Intersection'
                        with arcpy.da.UpdateCursor(junctions, ['PointType']) as DWcur:
                            for DWrow in DWcur:
                                DWrow[0] = 'DW Intersection'
                                DWcur.updateRow(DWrow)
                    else:
                        print 'Possible Error'
                        with arcpy.da.UpdateCursor(junctions, ['PointType']) as ucur:
                            for urow in ucur:
                                urow[0] = 'Investigate'
                                ucur.updateRow(urow)
                # print len(chklist)
                # print len(matching)
                # if jxy in chklist:
                #     print 'YES'
                    # print jxy, rdxy
                # else:
                #     print 'NO'
                    # print jxy, rdxy

            else:
                 arcpy.AddMessage('No road selected')
            arcpy.AddMessage('###   Finished Point   ###\n')
            arcpy.SelectLayerByAttribute_management(junctions, 'CLEAR_SELECTION')
            arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')





#                 for row in arcpy.da.SearchCursor(roads_lyr, ["SEGID", "SHAPE@"]):
#                     # Print the current line ID
#
#                     print("Feature {0}:".format(row[0]))
#
#                     # Set start point
#                     startpt = row[1].firstPoint
#
#                     # Set Start coordinates
#                     startx = startpt.X
#                     starty = startpt.Y
#
#                     # Set end point
#                     endpt = row[1].lastPoint
#
#                     # Set End coordinates
#                     endx = endpt.X
#                     endy = endpt.Y
#
#                     for pnt in row[1]:
#                         print("    Start Point: {}, {}".format(startx, starty))
#                         print("      End Point: {}, {}".format(endx, endy))
#
#
#
#
#
#
#
#
#
# totalval = int(arcpy.GetCount_management(endpoints).getOutput(0))
# if totalval > 0:
#     arcpy.AddIndex_management(endpoints, 'SEGID', 'SEGID_IDX')
#     arcpy.SelectLayerByAttribute_management(endpoints, 'CLEAR_SELECTION')
#     arcpy.SetProgressor('step', 'Examining Error Points For False Errors...', 0, totalval, 1)
#     with arcpy.da.SearchCursor(endpoints, ['SEGID']) as scur:
#         for row in scur:
#             arcpy.SetProgressorLabel('Loading SEGID:{0}...'.format(row[0]))
#             arcpy.AddMessage('###   Starting Error Point   ###')
#             arcpy.AddMessage("SEGID: " + str(row[0]))
#             arcpy.SelectLayerByAttribute_management(endpoints, 'NEW_SELECTION', "SEGID = " + str(row[0]))
#             arcpy.SelectLayerByLocation_management(roads_lyr, 'INTERSECT', endpoints)
#             selchk = int(arcpy.GetCount_management(roads_lyr).getOutput(0))
#             if selchk == 1:
#                 with arcpy.da.UpdateCursor(endpoints, ['PointType']) as ucur:
#                     for urow in ucur:
#                         urow[0] = 'Ignore'
#                         ucur.updateRow(urow)
#                 arcpy.SelectLayerByAttribute_management(endpoints, 'CLEAR_SELECTION')
#                 arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
#                 arcpy.AddMessage('Only one adjoining road - point will be ignored')
#                 arcpy.AddMessage('###   Finished Error Point   ###\n')
#
#             elif selchk == 2:
#                 with arcpy.da.SearchCursor(roads_lyr, ['SEGID', 'MUN_ID']) as rdcur:
#                     SEGlist = []
#                     MUNlist = []
#                     for rdrow in rdcur:
#                         rd0 = rdrow[0]
#                         rd1 = rdrow[1]
#                         SEGlist.append(str(rd0))
#                         MUNlist.append(str(rd1))
#                         arcpy.AddMessage('MUNID: ' + str(rd1))
#                     if MUNlist[0] == MUNlist[1] and SEGlist[0] == SEGlist[1]:
#                         with arcpy.da.UpdateCursor(endpoints, ['PointType']) as ucur:
#                             for urow in ucur:
#                                 urow[0] = 'Investigate'
#                                 ucur.updateRow(urow)
#                         arcpy.SelectLayerByAttribute_management(endpoints, 'CLEAR_SELECTION')
#                         arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
#                         arcpy.AddMessage('Matching MUNID & SEGID - Examine Point')
#                         arcpy.AddMessage('###   Finished Error Point   ###')
#                     if MUNlist[0] == MUNlist[1] and SEGlist[0] != SEGlist[1]:
#                         with arcpy.da.UpdateCursor(endpoints, ['PointType']) as ucur:
#                             for urow in ucur:
#                                 urow[0] = 'M_MUN D_SEG'
#                                 ucur.updateRow(urow)
#                         arcpy.SelectLayerByAttribute_management(endpoints, 'CLEAR_SELECTION')
#                         arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
#                         arcpy.AddMessage('Matching MUNID & Different SEGID - Examine Point')
#                         arcpy.AddMessage('###   Finished Error Point   ###')
#                     if MUNlist[0] != MUNlist[1] and SEGlist[0] == SEGlist[1]:
#                         with arcpy.da.UpdateCursor(endpoints, ['PointType']) as ucur:
#                             for urow in ucur:
#                                 urow[0] = 'D_MUN M_SEG'
#                                 ucur.updateRow(urow)
#                         arcpy.SelectLayerByAttribute_management(endpoints, 'CLEAR_SELECTION')
#                         arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
#                         arcpy.AddMessage('Different MUNID & Matching SEGID - Examine Point')
#                         arcpy.AddMessage('###   Finished Error Point   ###')
#                     if MUNlist[0] != MUNlist[1] and SEGlist[0] != SEGlist[1]:
#                         with arcpy.da.UpdateCursor(endpoints, ['PointType']) as ucur:
#                             for urow in ucur:
#                                 urow[0] = 'D_MUN D_SEG'
#                                 ucur.updateRow(urow)
#                         arcpy.SelectLayerByAttribute_management(endpoints, 'CLEAR_SELECTION')
#                         arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
#                         arcpy.AddMessage('Different MUNID & SEGID - Examine Point')
#                         arcpy.AddMessage('###   Finished Error Point   ###')
#             else:
#                 with arcpy.da.UpdateCursor(endpoints, ['PointType']) as upcur:
#                     for uprow in upcur:
#                         uprow[0] = '3 or more'
#                         upcur.updateRow(uprow)
#                 arcpy.SelectLayerByAttribute_management(endpoints, 'CLEAR_SELECTION')
#                 arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
#                 arcpy.AddMessage('3 or more segments')
#                 arcpy.AddMessage('###   Finished Error Point   ###\n')
#             arcpy.SetProgressorPosition()
#             arcpy.ResetProgressor()
#
#
#
#
#
# # Enter for loop for each feature
# #
# for row in arcpy.da.SearchCursor(roads_lyr, ["SEGID", "SHAPE@"]):
#     # Print the current line ID
#
#     print("Feature {0}:".format(row[0]))
#
#     #Set start point
#     startpt = row[1].firstPoint
#
#     #Set Start coordinates
#     startx = startpt.X
#     starty = startpt.Y
#
#     #Set end point
#     endpt = row[1].lastPoint
#
#     #Set End coordinates
#     endx = endpt.X
#     endy = endpt.Y
#
#     for pnt in row[1]:
#         print("    Start Point: {}, {}".format(startx, starty))
#         print("      End Point: {}, {}".format(endx, endy))
#
#
#
#
# else:
#     print('No records are selected')
# arcpy.SelectLayerByAttribute_management(junctions, 'CLEAR_SELECTION')
# arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
#
del arcpy
end_time = datetime.now()
elt = end_time - start_time

print "Start Time: " + str(start_time)
print "End Time: " + str(end_time)
print "Elapsed Time: " + str(elt)
print "Script complete"
#
#
#
#
#
#
#
#
#
#
#
#
# for row in arcpy.da.SearchCursor(junctions, ["JUNCTIONID", "SHAPE@"]):
#     # Print the current multipoint's ID
#     #
#     print("Feature {}:".format(row[0]))
#
#     # For each point in the multipoint feature,
#     #  print the x,y coordinates
#     for pnt in row[1]:
#         print("    {}, {}".format(pnt.X, pnt.Y))