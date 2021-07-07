import arcpy, os, sys
from datetime import *
start_time = datetime.now()
try:

    ws = arcpy.GetParameterAsText(0)
    #ws = r"N:\Users\ChrisHarlow\Projects\PseudoNodes\PseudoNodes.gdb"

    arcpy.env.overwriteOutput = True
    arcpy.env.XYTolerance = "0.0001 Meters"

    arcpy.env.workspace = ws
    today = str(date.today())
    day = today.replace('-', '')

    sr = arcpy.SpatialReference('NAD 1983 CSRS UTM Zone 20N')
    arcpy.CreateFeatureDataset_management(ws, 'PS_' + day, sr)
    arcpy.AddMessage(day + ' Feature Dataset Created')

    arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSCAF.NSCAF\NSCAF.nscaf_gsa', ws + os.sep + 'PS_' + day, 'GSA_' + day)
    arcpy.AddMessage('GSA Feature Class Imported')
    arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.blkpassage', ws + os.sep + 'PS_' + day, 'BlockedPassages_' + day)
    arcpy.AddMessage('Blocked Passages Feature Class Imported')
    arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.jinctions', ws + os.sep + 'PS_' + day, 'Junctions_' + day)
    arcpy.AddMessage('Blocked Passages Feature Class Imported')
    arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.nsrn', ws + os.sep + 'PS_' + day, 'NSRN_' + day)
    arcpy.AddMessage('NSRN Feature Classes Imported')

    arcpy.TableToTable_conversion(r'Database Connections\orcl1.sde\NSCAF.SEG_TAB', ws, 'SEGTAB_' + day)
    arcpy.AddMessage('SEG_TAB Table Imported')

    arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'GSA_' + day, ws + os.sep + 'PS_' + day + os.sep + 'GSAextracted_' + day, "RETIRED LIKE 'N'")
    arcpy.AddMessage('GSA Feature Class Selected')
    arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'BlockedPassages_' + day, ws + os.sep + 'PS_' + day + os.sep + 'BlockedPassagesextracted_' + day, "RETIRED LIKE 'N'")
    arcpy.AddMessage('Blocked Passages Feature Class Selected')
    arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'Junctions_' + day, ws + os.sep + 'PS_' + day + os.sep + 'Junctionsextracted_' + day, "RETIRED LIKE 'N'")
    arcpy.AddMessage('Junctions Feature Class Selected')
    arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'NSRN_' + day, ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, "RETIRED LIKE 'N' AND IDS > 0")
    arcpy.AddMessage('NSRN Feature Class Selected')

    arcpy.TableSelect_analysis(ws + os.sep + 'SEGTAB_' + day, ws + os.sep + 'SEGTABextracted_' + day, "RETIRED LIKE 'N'")
    arcpy.AddMessage('SEG_TAB Table Selected')

    arcpy.CreateTopology_management(ws + os.sep + 'PS_' + day, 'Topology_' + day, 0.001)
    arcpy.AddFeatureClassToTopology_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day, ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, 1, 1)
    arcpy.AddRuleToTopology_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day, 'Must Not Have Pseudo-Nodes (Line)', ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day)
    arcpy.AddRuleToTopology_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day, 'Must Not Have Dangles (Line)', ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day)
    arcpy.ValidateTopology_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day)
    arcpy.ExportTopologyErrors_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day, ws + os.sep + 'PS_' + day, 'Topology_' + day)
    arcpy.AddMessage('Topology Created')

    if int(arcpy.GetCount_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point').getOutput(0)) > 0:


        if int(arcpy.GetCount_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_line').getOutput(0)) > 0:
            arcpy.AddMessage('Not Removing ' + ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_line' + ' There Are Features In The File - Please Examine')
        else:
            arcpy.Delete_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_line')
            arcpy.AddMessage('Unused Line Feature Class Removed')
        if int(arcpy.GetCount_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_poly').getOutput(0)) > 0:
            arcpy.AddMessage('Not Removing ' + ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_poly' + ' There Are Features In The File - Please Examine')
        else:
            arcpy.Delete_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_poly')
            arcpy.AddMessage('Unused Poly Feature Class Removed')
        #
        arcpy.AddField_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', 'ErrorType', 'TEXT')
        arcpy.AddMessage('ErrorType Field Added')

        arcpy.JoinField_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, 'SEGID', ws + os.sep + 'SEGTABextracted_' + day, 'SEGID', ['OWNER'])
        arcpy.AddMessage('Owner Field Added')

        errorpts_lyr = 'errorpts_lyr'
        arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', errorpts_lyr, "RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
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

        arcpy.Compact_management(ws)

        def validbreaks(field, calculate):
            global errorpts_lyr, roads_lyr
            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'NEW_SELECTION', "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
            totalval = int(arcpy.GetCount_management(errorpts_lyr).getOutput(0))
            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
            arcpy.SetProgressor('step', 'Examining Error Points For False Errors...', 0, totalval, 1)
            with arcpy.da.SearchCursor(errorpts_lyr, ['OID@', 'ErrorType'], 'ErrorType IS NULL') as scur:
                for row in scur:
                    arcpy.SetProgressorLabel('Loading OID:{0} for {1} field...'.format(row[0], field))
                    arcpy.AddMessage('###   Starting Error Point   ###')
                    arcpy.AddMessage("OID: " + str(row[0]))
                    arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'NEW_SELECTION', "OID = " + str(row[0]))
                    arcpy.SelectLayerByLocation_management(roads_lyr, 'INTERSECT', errorpts_lyr)
                    with arcpy.da.SearchCursor(roads_lyr, [field]) as roadcur:
                        chklist = []
                        for rdrow in roadcur:
                            rd1 = rdrow[0]
                            chklist.append(str(rd1))
                            arcpy.AddMessage(field + ": " + str(rd1))
                        if chklist[0] == chklist[1]:
                            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
                            arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
                            arcpy.AddMessage('Values match - Possible error')
                            arcpy.AddMessage('###   Finished Error Point   ###\n')
                        else:
                            with arcpy.da.UpdateCursor(errorpts_lyr, ['OID@', 'ErrorType'], "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'") as ucur:
                                for urow in ucur:
                                    urow[1] = calculate
                                    ucur.updateRow(urow)
                            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
                            arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
                            arcpy.AddMessage('Values are different - False error')
                            arcpy.AddMessage('###   Finished Error Point   ###\n')
                    arcpy.SetProgressorPosition()
            arcpy.ResetProgressor()
            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
            arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
            return


        def rdmatch(field, val, calculate):
            global errorpts_lyr, roads_lyr
            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'NEW_SELECTION', "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
            totalval = int(arcpy.GetCount_management(errorpts_lyr).getOutput(0))
            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
            arcpy.SetProgressor('step', 'Examining Error Points For False Errors...', 0, totalval, 1)
            with arcpy.da.SearchCursor(errorpts_lyr, ['OID@', 'ErrorType'], 'ErrorType IS NULL') as scur:
                for row in scur:
                    arcpy.SetProgressorLabel('Loading OID:{0} for {1} field...'.format(row[0], field))
                    arcpy.AddMessage('\n###   Starting Error Point   ###')
                    arcpy.AddMessage("OID: " + str(row[0]))
                    arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'NEW_SELECTION', "OID = " + str(row[0]))
                    arcpy.SelectLayerByLocation_management(roads_lyr, 'INTERSECT', errorpts_lyr)
                    with arcpy.da.SearchCursor(roads_lyr, [field]) as rdcur:
                        chklist = []
                        for rdrow in rdcur:
                            rd1 = rdrow[0]
                            chklist.append(str(rd1))
                            arcpy.AddMessage(field + ": " + str(rd1))
                        if chklist[0] == val and chklist[1] == val:
                            with arcpy.da.UpdateCursor(errorpts_lyr, ['OID@', 'ErrorType'], "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'") as ucur:
                                for urow in ucur:
                                    urow[1] = calculate
                                    ucur.updateRow(urow)
                            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
                            arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
                            arcpy.AddMessage('Values match - False error')
                            arcpy.AddMessage('###   Finished Error Point   ###')
                        else:
                            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
                            arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
                            arcpy.AddMessage('Values are different - Possible error')
                            arcpy.AddMessage('###   Finished Error Point   ###')
                    arcpy.SetProgressorPosition()
            arcpy.ResetProgressor()
            arcpy.SelectLayerByAttribute_management(errorpts_lyr, 'CLEAR_SELECTION')
            arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')
            return



        arcpy.Compact_management(ws)


        validbreaks('ROADCLASS', 'Road Class Change')
        arcpy.AddMessage('Matching Road Class Errors Classified')
        validbreaks('OWNER', 'Owner Change')
        arcpy.AddMessage('Matching Owner Errors Classified')
        validbreaks('MUN_ID', 'MUNID Change')
        arcpy.AddMessage('Matching MUNID Errors Classified')
        validbreaks('STREET', 'Street Name Change')
        arcpy.AddMessage('Matching Street Name Errors Classified')
        rdmatch('ROADCLASS', 'DW', 'Dry Weather')
        arcpy.AddMessage('Dry Weather Roads Classified')
        rdmatch('ROADCLASS', 'WA', 'Water Access')
        arcpy.AddMessage('Water Access Roads Classified')


        viewpts = 'viewpoints'
        arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', viewpts, "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
        arcpy.CalculateField_management(viewpts, 'ErrorType', "'Investigate'", 'PYTHON')

        arcpy.Compact_management(ws)

        arcpy.AddMessage('Processing Dangles')
        errorpts_lyr_dangles = 'errorpts_lyr_dangles'
        arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', errorpts_lyr_dangles, "RuleDescription LIKE 'Must Not Have Dangles'")

        roads_lyr_DW = 'roads_lyr2'
        arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr_DW, "ROADCLASS = 'DW'")
        arcpy.AddMessage('Selecting Roads - Dry Weather')
        arcpy.SelectLayerByLocation_management(errorpts_lyr_dangles, 'INTERSECT', roads_lyr_DW)
        dw_chk = int(arcpy.GetCount_management(errorpts_lyr_dangles)[0])
        if dw_chk == 0:
            arcpy.AddMessage('No Dry Weather Roads Match Any Topology Error Points')
        else:
            arcpy.AddMessage('Marking Features to Ignore')
            arcpy.CalculateField_management(errorpts_lyr_dangles, 'ErrorType', "'Dry Weather'", 'PYTHON')
            arcpy.SelectLayerByAttribute_management(errorpts_lyr_dangles, 'CLEAR_SELECTION')
            arcpy.SelectLayerByAttribute_management(roads_lyr_DW, 'CLEAR_SELECTION')
            del roads_lyr_DW

        roads_lyr_WA = 'roads_lyr3'
        arcpy.AddMessage('Selecting Roads - Water Access')
        arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr_WA, "ROADCLASS = 'WA'")
        arcpy.SelectLayerByLocation_management(errorpts_lyr_dangles, 'INTERSECT', roads_lyr_WA)
        wa_chk = int(arcpy.GetCount_management(errorpts_lyr_dangles)[0])
        if wa_chk == 0:
            arcpy.AddMessage('No Water Access Roads Match Any Topology Error Points')
        else:
            arcpy.AddMessage('Marking Features to Ignore')
            arcpy.CalculateField_management(errorpts_lyr_dangles, 'ErrorType', "'Water Access'", 'PYTHON')
            arcpy.SelectLayerByAttribute_management(errorpts_lyr_dangles, 'CLEAR_SELECTION')
            arcpy.SelectLayerByAttribute_management(roads_lyr_WA, 'CLEAR_SELECTION')
            del roads_lyr_WA


        errorpts_lyr_dangles_NULL = 'errorpts_lyr_dangles_NULL'
        arcpy.arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', errorpts_lyr_dangles_NULL, "RuleDescription LIKE 'Must Not Have Dangles' AND ErrorType IS NULL")

        epdn_chk = int(arcpy.GetCount_management(errorpts_lyr_dangles_NULL)[0])
        if epdn_chk == 0:
            arcpy.AddMessage('No Dangle Error Points Can Be Processed - None Are NULL')
        else:
            arcpy.AddMessage('Buffering Possible Errors')
            arcpy.Buffer_analysis(errorpts_lyr_dangles_NULL, ws + os.sep + 'PS_' + day + os.sep + 'Buffer_' + day, '5 Meters')
            buff_pts = 'buffer_pts'
            arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'Buffer_' + day, buff_pts)
            arcpy.SelectLayerByLocation_management(roads_lyr, 'INTERSECT', buff_pts)
            buf_chk = int(arcpy.GetCount_management(roads_lyr)[0])
            if buf_chk == 0:
                arcpy.AddMessage('No Roads Touch Any Buffers')
            else:
                arcpy.AddMessage('Identifying Errors')
                arcpy.SelectLayerByLocation_management(roads_lyr, 'INTERSECT', errorpts_lyr_dangles_NULL, selection_type="REMOVE_FROM_SELECTION")
                rd_chk = int(arcpy.GetCount_management(roads_lyr)[0])
                if rd_chk == 0:
                    arcpy.AddMessage("No Roads Touch Dangle Error Points")
                else:
                    arcpy.SelectLayerByLocation_management(buff_pts, 'INTERSECT', roads_lyr, selection_type='NEW_SELECTION')
                    rd_buf_chk = int(arcpy.GetCount_management(roads_lyr)[0])
                    if rd_buf_chk == 0:
                        arcpy.AddMessage("No buffers Intersect The Current Road Selection")
                    else:
                        arcpy.SelectLayerByLocation_management(errorpts_lyr_dangles_NULL, "WITHIN", buff_pts, selection_type='NEW_SELECTION')
                        arcpy.CalculateField_management(errorpts_lyr_dangles_NULL, 'ErrorType', "'Investigate'", 'PYTHON')
                        arcpy.AddMessage('Dangle Errors Identified - They Are Marked With Investigate')
        arcpy.Compact_management(ws)

    else:
        arcpy.AddMessage('Congratulations!  There Are No Pseudo Nodes')
except Exception, e:
    tb = sys.exc_info()[2]
    arcpy.AddMessage("Line %i" % tb.tb_lineno)
    arcpy.AddMessage(e.message)
del arcpy
