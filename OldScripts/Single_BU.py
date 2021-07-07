import arcpy, os, sys
from datetime import *
start_time = datetime.now()
try:

    # ws = arcpy.GetParameterAsText(0)
    ws = r"D:\Work\PseudoNodes\PseudoNodes.gdb"

    arcpy.env.overwriteOutput = True

    arcpy.env.workspace = ws
    today = str(date.today())
    day = today.replace('-', '')

    sr = arcpy.SpatialReference('NAD 1983 CSRS UTM Zone 20N')
    arcpy.CreateFeatureDataset_management(ws, 'PS_' + day, sr)
    arcpy.AddMessage('Feature Dataset Created')

    arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSCAF.NSCAF\NSCAF.nscaf_gsa', ws + os.sep + 'PS_' + day, 'GSA_' + day)
    arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.blkpassage', ws + os.sep + 'PS_' + day, 'BlockedPassages_' + day)
    arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.nsrn', ws + os.sep + 'PS_' + day, 'NSRN_' + day)
    arcpy.AddMessage('Feature Classes Imported')

    arcpy.TableToTable_conversion(r'Database Connections\orcl1.sde\NSCAF.SEG_TAB', ws, 'SEGTAB_' + day)
    arcpy.AddMessage('Table Imported')

    arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'GSA_' + day, ws + os.sep + 'PS_' + day + os.sep + 'GSAextracted_' + day, "RETIRED LIKE 'N'")
    arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'BlockedPassages_' + day, ws + os.sep + 'PS_' + day + os.sep + 'BlockedPassagesextracted_' + day, "RETIRED LIKE 'N'")
    arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'NSRN_' + day, ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, "RETIRED LIKE 'N' AND IDS > 0")
    arcpy.AddMessage('Feature Classes Selected')

    arcpy.TableSelect_analysis(ws + os.sep + 'SEGTAB_' + day, ws + os.sep + 'SEGTABextracted_' + day, "RETIRED LIKE 'N'")
    arcpy.AddMessage('Table Selected')

    arcpy.CreateTopology_management(ws + os.sep + 'PS_' + day, 'Topology_' + day, 0.001)
    arcpy.AddFeatureClassToTopology_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day, ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, 1, 1)
    arcpy.AddRuleToTopology_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day, 'Must Not Have Pseudo-Nodes (Line)', ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day)
    arcpy.ValidateTopology_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day)
    arcpy.ExportTopologyErrors_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day, ws + os.sep + 'PS_' + day, 'Topology_' + day)
    arcpy.AddMessage('Topology Created')

    if int(arcpy.GetCount_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point').getOutput(0)) > 0:


        if int(arcpy.GetCount_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_line').getOutput(0)) > 0:
            arcpy.AddMessage('Not Removing ' + ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_line' + ' There Are Features In The File - Please Examine')
        else:
            arcpy.Delete_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_line')
            arcpy.AddMessage('Unused Feature Class Removed')
        if int(arcpy.GetCount_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_poly').getOutput(0)) > 0:
            arcpy.AddMessage('Not Removing ' + ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_poly' + ' There Are Features In The File - Please Examine')
        else:
            arcpy.Delete_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_poly')
            arcpy.AddMessage('Unused Feature Class Removed')

        arcpy.AddField_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', 'ErrorType', 'TEXT')
        arcpy.AddMessage('Field Added')

        arcpy.JoinField_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, 'SEGID', ws + os.sep + 'SEGTABextracted_' + day, 'SEGID', ['OWNER'])
        arcpy.AddMessage('Field Added')

        errorpts_lyr = 'errorpts_lyr'
        arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', errorpts_lyr)
        gsa_lyr = 'gsa_lyr'
        arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'GSAextracted_' + day, gsa_lyr)
        blkpsg_lyr = 'blkpsg_lyr'
        arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'BlockedPassagesextracted_' + day, blkpsg_lyr)
        roads_lyr = 'roads_lyr'
        arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr)
        arcpy.AddMessage('Feature Layers Created')

        arcpy.SelectLayerByLocation_management(errorpts_lyr, 'ARE_IDENTICAL_TO', blkpsg_lyr)
        blk_chk = int(arcpy.GetCount_management(errorpts_lyr)[0])
        if blk_chk == 0:
            arcpy.AddMessage('No Blocked Passages Match Any Topology Error Points')
        else:
            arcpy.CalculateField_management(errorpts_lyr, 'ErrorType', "'Blocked Passage'", 'PYTHON')
            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
            arcpy.SelectLayerByAttribute_management(blkpsg_lyr, 'CLEAR_SELECTION')

        arcpy.SelectLayerByLocation_management(errorpts_lyr, 'BOUNDARY_TOUCHES', gsa_lyr)
        gsa_chk = int(arcpy.GetCount_management(errorpts_lyr)[0])
        if gsa_chk == 0:
            arcpy.AddMessage('No GSA Boundaries Intersect Any Topology Error Points')
        else:
            arcpy.CalculateField_management(errorpts_lyr, 'ErrorType', "'Community Boundary'", 'PYTHON')
            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
            arcpy.SelectLayerByAttribute_management(gsa_lyr, 'CLEAR_SELECTION')
        arcpy.AddMessage('Initial Classifications Are Done')

        arcpy.AddIndex_management(errorpts_lyr, ['OriginObjectID', 'DestinationObjectID'], 'errorpts_' + day)
        arcpy.AddIndex_management(roads_lyr, ['OWNER', 'MUNID', 'ROADCLASS', 'STREET', 'SEGID'], 'rds_' + day)
        arcpy.AddMessage('Indexes Added')


        def validbreaks(field, calculate):
            global errorpts_lyr, roads_lyr
            totalval = int(arcpy.GetCount_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point').getOutput(0))
            arcpy.SetProgressor('step', 'Examining Error Points For False Errors...', 0, totalval, 1)
            with arcpy.da.SearchCursor(errorpts_lyr, ['OriginObjectID', 'DestinationObjectID']) as scur:
                for row in scur:
                    arcpy.SetProgressorLabel('Loading OriginObjectID:{0} and DestinationObjectID:{1}...'.format(row[0], row[1]))
                    sfeat1 = row[0]
                    sfeat2 = row[1]
                    arcpy.AddMessage('###   Starting Error Point   ###')
                    arcpy.AddMessage("Origin ObjectID:      " + str(sfeat1))
                    arcpy.AddMessage("Destination ObjectID: " + str(sfeat2))
                    arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'NEW_SELECTION', "OriginObjectID = " + str(sfeat1) + " OR DestinationObjectID = " + str(sfeat2) + " AND ErrorType IS NULL")
                    rdchk = int(arcpy.GetCount_management(errorpts_lyr)[0])
                    if rdchk == 1:
                        arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
                        arcpy.SelectLayerByAttribute_management(roads_lyr, 'NEW_SELECTION', "OBJECTID = " + str(sfeat1) + " OR OBJECTID = " + str(sfeat2) + " ")
                        with arcpy.da.SearchCursor(roads_lyr, [field]) as roadcur:
                            chklist = []
                            for rdrow in roadcur:
                                rd1 = rdrow[0]
                                chklist.append(str(rd1))
                                arcpy.AddMessage(field + ": " + str(rd1))
                            if chklist[0] == chklist[1]:
                                arcpy.AddMessage('Values match - Possible error')
                                arcpy.AddMessage('###   Finished Error Point   ###\n')
                            else:
                                arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'NEW_SELECTION', "OriginObjectID = " + str(sfeat1) + " OR DestinationObjectID = " + str(sfeat2))
                                arcpy.CalculateField_management(errorpts_lyr, 'ErrorType', calculate, 'PYTHON')
                                arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
                                arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
                                arcpy.AddMessage('Values are different - False error')
                                arcpy.AddMessage('###   Finished Error Point   ###\n')
                    else:
                        arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
                        arcpy.AddMessage('Error Point Has Already Been Classified')
                        arcpy.AddMessage('###   Finished Error Point   ###\n')
                    arcpy.SetProgressorPosition()
            arcpy.ResetProgressor()
            del row, scur, rdrow, roadcur
            return


        def rdmatch(field, val, calculate):
            global errorpts_lyr, roads_lyr
            totalval = int(arcpy.GetCount_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point').getOutput(0))
            arcpy.SetProgressor('step', 'Examining Error Points For False Errors...', 0, totalval, 1)
            with arcpy.da.SearchCursor(errorpts_lyr, ['OriginObjectID', 'DestinationObjectID']) as scur:
                for row in scur:
                    arcpy.SetProgressorLabel('Loading OriginObjectID:{0} and DestinationObjectID:{1}...'.format(row[0], row[1]))
                    sfeat1 = row[0]
                    sfeat2 = row[1]
                    arcpy.AddMessage('###   Starting Error Point   ###')
                    arcpy.AddMessage("Origin ObjectID:      " + str(sfeat1))
                    arcpy.AddMessage("Destination ObjectID: " + str(sfeat2))
                    arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'NEW_SELECTION', "OriginObjectID = " + str(sfeat1) + " OR DestinationObjectID = " + str(sfeat2) + " AND ErrorType IS NULL")
                    rdchk = int(arcpy.GetCount_management(errorpts_lyr)[0])
                    if rdchk == 1:
                        arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
                        arcpy.SelectLayerByAttribute_management(roads_lyr, 'NEW_SELECTION', "OBJECTID = " + str(sfeat1) + " OR OBJECTID = " + str(sfeat2))
                        with arcpy.da.SearchCursor(roads_lyr, [field]) as rdcur:
                            chklist = []
                            for rdrow in rdcur:
                                rd1 = rdrow[0]
                                chklist.append(str(rd1))
                                arcpy.AddMessage(field + ": " + str(rd1))
                            if chklist[0] == val and chklist[1] == val:
                                arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'NEW_SELECTION', "OriginObjectID = " + str(sfeat1) + " OR DestinationObjectID = " + str(sfeat2))
                                arcpy.CalculateField_management(errorpts_lyr, 'ErrorType', calculate, 'PYTHON')
                                arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
                                arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
                                arcpy.AddMessage('Values match - False error')
                                arcpy.AddMessage('###   Finished Error Point   ###\n')
                            else:
                                arcpy.AddMessage('Values are different - Possible error')
                                arcpy.AddMessage('###   Finished Error Point   ###\n')
                    else:
                        arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
                        arcpy.AddMessage('Error Point Has Already Been Classified')
                        arcpy.AddMessage('###   Finished Error Point   ###\n')
                    arcpy.SetProgressorPosition()
            arcpy.ResetProgressor()
            del row, scur, rdrow, rdcur
            return


        arcpy.Compact_management(ws)


        # validbreaks('ROADCLASS', "'Road Class Change'")
        # arcpy.AddMessage('Matching Road Class Errors Classified')
        # validbreaks('OWNER', "'Owner Change'")
        # arcpy.AddMessage('Matching Owner Errors Classified')
        # validbreaks('MUN_ID', "'MUNID Change'")
        # arcpy.AddMessage('Matching MUNID Errors Classified')
        # validbreaks('STREET', "'Street Name Change'")
        # arcpy.AddMessage('Matching Street Name Errors Classified')
        #
        # rdmatch('ROADCLASS', 'DW', "'Dry Weather'")
        # arcpy.AddMessage('Dry Weather Roads Classified')
        # rdmatch('ROADCLASS', 'WA', "'Water Access'")
        # arcpy.AddMessage('Water Access Roads Classified')

        arcpy.Compact_management(ws)


    else:
        arcpy.AddMessage('Congratulations!  There Are No Pseudo Nodes')



    del roads_lyr, errorpts_lyr, blkpsg_lyr, gsa_lyr
except Exception, e:
    tb = sys.exc_info()[2]
    arcpy.AddMessage("Line %i" % tb.tb_lineno)
    arcpy.AddMessage(e.message)
end_time = datetime.now()
elt = end_time - start_time
print "\n Start Time: ", start_time
print "End Time: ", end_time
print "Elapsed Time: ", elt
print "Script complete.\n"
