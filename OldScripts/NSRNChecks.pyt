import arcpy, os, sys
from datetime import *
start_time = datetime.now()


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "NSRNChecks"
        self.alias = "NSRN Checks"

        # List of tool classes associated with this toolbox
        self.tools = [Dataprep, PseudoNodes, Dangles, DissolvedSEGID, LRS, SEGID]

class Dataprep(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1. Data Prep"
        self.description = "The tool used to prepare and download the required data for the NSRN checks"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input Workspace",
            name="in_ws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        try:
            # """The source code of the tool."""
            # ws = str(parameters[0].value)
            # arcpy.AddMessage(ws)
            # 
            # arcpy.env.overwriteOutput = True
            # arcpy.env.XYTolerance = "0.0001 Meters"
            # 
            # today = str(date.today())
            # day = today.replace('-', '')
            # 
            # sr = arcpy.SpatialReference('NAD 1983 CSRS UTM Zone 20N')
            # arcpy.CreateFeatureDataset_management(ws, 'Data_' + day, sr)
            # arcpy.AddMessage(day + ' Feature Dataset Created')
            # 
            # arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSCAF.NSCAF\NSCAF.nscaf_gsa', ws + os.sep + 'Data_' + day, 'GSA_' + day)
            # arcpy.AddMessage('GSA Feature Class Imported')
            # arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.blkpassage', ws + os.sep + 'Data_' + day, 'BlockedPassages_' + day)
            # arcpy.AddMessage('Blocked Passages Feature Class Imported')
            # arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.junctions', ws + os.sep + 'Data_' + day, 'Junctions_' + day)
            # arcpy.AddMessage('Junctions Feature Class Imported')
            # arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.nsrn', ws + os.sep + 'Data_' + day, 'NSRN_' + day)
            # arcpy.AddMessage('NSRN Feature Classes Imported')
            # 
            # arcpy.TableToTable_conversion(r'Database Connections\orcl1.sde\NSCAF.SEG_TAB', ws, 'SEGTAB_' + day)
            # arcpy.AddMessage('SEG_TAB Table Imported')
            # 
            # arcpy.TableToTable_conversion(r'Database Connections\orcl1.sde\NSRN.LRS', ws, 'LRS_' + day)
            # arcpy.AddMessage('LRS Table Imported')
            # 
            # arcpy.Select_analysis(ws + os.sep + 'Data_' + day + os.sep + 'GSA_' + day, ws + os.sep + 'Data_' + day + os.sep + 'GSAextracted_' + day, "RETIRED LIKE 'N'")
            # arcpy.AddMessage('GSA Feature Class Selected')
            # arcpy.Select_analysis(ws + os.sep + 'Data_' + day + os.sep + 'BlockedPassages_' + day, ws + os.sep + 'Data_' + day + os.sep + 'BlockedPassagesextracted_' + day, "RETIRED LIKE 'N'")
            # arcpy.AddMessage('Blocked Passages Feature Class Selected')
            # arcpy.Select_analysis(ws + os.sep + 'Data_' + day + os.sep + 'Junctions_' + day, ws + os.sep + 'Data_' + day + os.sep + 'Junctionsextracted_' + day, "RETIRED LIKE 'N'")
            # arcpy.AddMessage('Junctions Feature Class Selected')
            # arcpy.Select_analysis(ws + os.sep + 'Data_' + day + os.sep + 'NSRN_' + day, ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day, "RETIRED LIKE 'N' AND IDS > 0")
            # arcpy.AddMessage('NSRN Feature Class Selected')
            # 
            # arcpy.TableSelect_analysis(ws + os.sep + 'SEGTAB_' + day, ws + os.sep + 'SEGTABextracted_' + day, "RETIRED LIKE 'N'")
            # arcpy.AddMessage('SEG_TAB Table Selected')
            # 
            # arcpy.TableSelect_analysis(ws + os.sep + 'LRS_' + day, ws + os.sep + 'LRSextracted_' + day, "RETIRED LIKE 'N'")
            # arcpy.AddMessage('LRS Table Selected')
            # 
            # arcpy.AddField_management(ws + os.sep + 'Data_' + day + os.sep + 'Junctionsextracted_' + day, 'ErrorType', 'TEXT')
            # arcpy.AddField_management(ws + os.sep + 'LRSextracted_' + day, 'ErrorType', 'TEXT')
            # arcpy.AddMessage('Error Type Field Added')



            arcpy.CreateTopology_management(ws + os.sep + 'Data_' + day, 'Topology_' + day, 0.001)
            arcpy.AddFeatureClassToTopology_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day, ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day, 1, 1)
            arcpy.AddRuleToTopology_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day, 'Must Not Have Pseudo-Nodes (Line)', ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day)
            arcpy.AddRuleToTopology_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day, 'Must Not Have Dangles (Line)', ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day)
            arcpy.ValidateTopology_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day)
            arcpy.ExportTopologyErrors_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day, ws + os.sep + 'Data_' + day, 'Topology_' + day)
            arcpy.AddMessage('Topology Created')

            if int(arcpy.GetCount_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_point').getOutput(0)) > 0:

                if int(arcpy.GetCount_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_line').getOutput(0)) > 0:
                    arcpy.AddMessage('Not Removing ' + ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_line' + ' There Are Features In The File - Please Examine')
                else:
                    arcpy.Delete_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_line')
                    arcpy.AddMessage('Unused Line Feature Class Removed')
                if int(arcpy.GetCount_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_poly').getOutput(0)) > 0:
                    arcpy.AddMessage('Not Removing ' + ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_poly' + ' There Are Features In The File - Please Examine')
                else:
                    arcpy.Delete_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_poly')
                    arcpy.AddMessage('Unused Poly Feature Class Removed')

                arcpy.AddField_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_point', 'ErrorType', 'TEXT')
                arcpy.AddMessage('ErrorType Field Added')

                # arcpy.JoinField_management(ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day, 'SEGID', ws + os.sep + 'SEGTABextracted_' + day, 'SEGID', ['OWNER'])
                # arcpy.AddMessage('Owner Field Added')
            else:
                arcpy.AddMessage('Congratulations!  There Are No Topological Errors')


        except Exception, e:
            tb = sys.exc_info()[2]
            arcpy.AddMessage("Line %i" % tb.tb_lineno)
            arcpy.AddMessage(e.message)

        return

class PseudoNodes(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2. Pseudo Nodes"
        self.description = "The tool used to locate any pseudo nodes from the topology"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input Workspace",
            name="in_ws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        try:
            ws = str(parameters[0].value)
            arcpy.AddMessage(ws)

            arcpy.env.overwriteOutput = True
            arcpy.env.XYTolerance = "0.0001 Meters"

            today = str(date.today())
            day = today.replace('-', '')

            datechk = arcpy.Exists(ws + os.sep + 'Data_' + day)
            if datechk is True:
                arcpy.AddMessage('Data Folder Found - Processing Will Begin')
                if int(arcpy.GetCount_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_point').getOutput(0)) > 0:
                    errorpts_lyr = 'errorpts_lyr'
                    arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_point', errorpts_lyr, "RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
                    gsa_lyr = 'gsa_lyr'
                    arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'GSAextracted_' + day, gsa_lyr)
                    blkpsg_lyr = 'blkpsg_lyr'
                    arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'BlockedPassagesextracted_' + day, blkpsg_lyr)
                    roads_lyr = 'roads_lyr'
                    arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr)
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
                        #global errorpts_lyr, roads_lyr
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
                        #global errorpts_lyr, roads_lyr
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
                    arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_point', viewpts,
                                                      "ErrorType IS NULL AND RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
                    arcpy.CalculateField_management(viewpts, 'ErrorType', "'Investigate'", 'PYTHON')

                    arcpy.Compact_management(ws)
            else:
                arcpy.AddMessage('Data Folder Not Found - Run Data Prep First')





        except Exception, e:
            tb = sys.exc_info()[2]
            arcpy.AddMessage("Line %i" % tb.tb_lineno)
            arcpy.AddMessage(e.message)





        return

class Dangles(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "3. Dangles"
        self.description = "The tool used to locate any dangles found in the topology"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input Workspace",
            name="in_ws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        try:
            ws = str(parameters[0].value)
            arcpy.AddMessage(ws)

            arcpy.env.overwriteOutput = True
            arcpy.env.XYTolerance = "0.0001 Meters"

            today = str(date.today())
            day = today.replace('-', '')

            datechk = arcpy.Exists(ws + os.sep + 'Data_' + day)
            if datechk is True:
                arcpy.AddMessage('Data Folder Found - Processing Will Begin')
                if int(arcpy.GetCount_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_point').getOutput(0)) > 0:
                    arcpy.AddMessage('Processing Dangles')
                    errorpts_lyr_dangles = 'errorpts_lyr_dangles'
                    arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_point', errorpts_lyr_dangles, "RuleDescription LIKE 'Must Not Have Dangles'")
                    roads_lyr = 'roads_lyr'
                    arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr)

                    roads_lyr_DW = 'roads_lyr2'
                    arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr_DW, "ROADCLASS = 'DW'")
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
                    arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr_WA, "ROADCLASS = 'WA'")
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
                    arcpy.arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'Topology_' + day + '_point', errorpts_lyr_dangles_NULL,
                                                            "RuleDescription LIKE 'Must Not Have Dangles' AND ErrorType IS NULL")

                    epdn_chk = int(arcpy.GetCount_management(errorpts_lyr_dangles_NULL)[0])
                    if epdn_chk == 0:
                        arcpy.AddMessage('No Dangle Error Points Can Be Processed - None Are NULL')
                    else:
                        arcpy.AddMessage('Buffering Possible Errors')
                        arcpy.Buffer_analysis(errorpts_lyr_dangles_NULL, ws + os.sep + 'Data_' + day + os.sep + 'Buffer_' + day, '5 Meters')
                        buff_pts = 'buffer_pts'
                        arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'Buffer_' + day, buff_pts)
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
                    arcpy.AddMessage('Data Folder Not Found - Run Data Prep First')



        except Exception, e:
            tb = sys.exc_info()[2]
            arcpy.AddMessage("Line %i" % tb.tb_lineno)
            arcpy.AddMessage(e.message)
        return

class DissolvedSEGID(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "4. Dissolved SEGID"
        self.description = "The tool used to find any SEGIDs that are duplicates"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input Workspace",
            name="in_ws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        try:
            ws = str(parameters[0].value)
            arcpy.AddMessage(ws)

            arcpy.env.overwriteOutput = True
            arcpy.env.XYTolerance = "0.0001 Meters"

            today = str(date.today())
            day = today.replace('-', '')

            datechk = arcpy.Exists(ws + os.sep + 'Data_' + day)
            if datechk is True:
                arcpy.AddMessage('Data Folder Found - Processing Will Begin')

                roads_lyr = 'roads'
                arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr, '"SEGID" <> 0')

                arcpy.Dissolve_management(roads_lyr, ws + os.sep + 'Data_' + day + os.sep + 'NSRNDissolved_' + day, "SEGID", multi_part="SINGLE_PART")
                del roads_lyr
                arcpy.AddIndex_management(ws + os.sep + 'Data_' + day + os.sep + 'NSRNDissolved_' + day, ['SEGID'], 'dissolved_' + day)

                roads_lyr2 = 'roads2'
                arcpy.Statistics_analysis(ws + os.sep + 'Data_' + day + os.sep + 'NSRNDissolved_' + day, ws + os.sep + 'NSRNDissolvedStatistics_' + day, "SEGID COUNT", "SEGID")
                arcpy.AddIndex_management(ws + os.sep + 'NSRNDissolvedStatistics_' + day, ['SEGID'], 'dissolvedtable_' + day)
                arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'NSRNDissolved_' + day, roads_lyr2, )

                arcpy.AddJoin_management(roads_lyr2, 'SEGID', ws + os.sep + 'NSRNDissolvedStatistics_' + day, 'SEGID')
                arcpy.SelectLayerByAttribute_management(roads_lyr2, 'NEW_SELECTION', 'FREQUENCY > 1')
                freqchk = int(arcpy.GetCount_management(roads_lyr2)[0])
                if freqchk == 0:
                    arcpy.AddMessage('No SEGIDs have more than one dissolved segment')
                else:
                    arcpy.AddMessage('There are features needing repair')
                    arcpy.CopyFeatures_management(roads_lyr2, ws + os.sep + 'Data_' + day + os.sep + 'NSRN_SEGIDdissolve_' + day)
                    arcpy.Compact_management(ws)
            else:
                arcpy.AddMessage('Data Folder Not Found - Run Data Prep First')


        except Exception, e:
            tb = sys.exc_info()[2]
            arcpy.AddMessage("Line %i" % tb.tb_lineno)
            arcpy.AddMessage(e.message)
        return

class LRS(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "5. LRS Check"
        self.description = "This tool checks the LRS table for records that are less than 5m.  Specifically those that are less than 2.5m will be corrected."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input Workspace",
            name="in_ws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        try:

            ws = str(parameters[0].value)
            arcpy.AddMessage(ws)

            arcpy.env.overwriteOutput = True
            arcpy.env.XYTolerance = "0.0001 Meters"

            today = str(date.today())
            day = today.replace('-', '')

            datechk = arcpy.Exists(ws + os.sep + 'Data_' + day)
            if datechk is True:
                arcpy.AddMessage('Data Folder Found - Processing Will Begin')

                LRS_Tab = ws + os.sep + 'LRSextracted_' + day

                def lrscheck(distance):
                    arcpy.MakeTableView_management(LRS_Tab, 'LTV', 'ErrorType IS NULL')
                    with arcpy.da.SearchCursor('LTV', ['ROADSEGID', 'IDS', 'START_DIST', 'STOP_DIST']) as cur:
                        for row in cur:
                            arcpy.AddMessage( '### Processing ###')
                            arcpy.AddMessage( '       SEGID: ' + str(row[0]))
                            arcpy.AddMessage( '         IDS: ' + str(row[1]))
                            arcpy.AddMessage( '  Start Dist: ' + str(row[2]))
                            arcpy.AddMessage( '   Stop Dist: ' + str(row[3]))
                            arcpy.AddMessage( 'Difference: ' + str(abs(row[3]) - abs(row[2])))
                            if abs(row[3]) - abs(row[2]) <= distance:
                                arcpy.AddMessage( ' ERROR - LRS RECORD NEEDS TO BE EXAMINED')
                                arcpy.AddMessage( ' SEGMENT IS LESS THAN ' + str(distance) + ' METRES')
                                with arcpy.da.UpdateCursor(LRS_Tab, ['ErrorType'], 'ROADSEGID = ' + str(int(row[0]))) as ucur:
                                    for urow in ucur:
                                        urow[0] = 'Possible Error'
                                        ucur.updateRow(urow)
                            arcpy.AddMessage( '###   Done   ###\n')
                    arcpy.Delete_management('LTV')
                    return
                lrscheck(2.5)
                lrscheck(5)
            else:
                arcpy.AddMessage('Data Folder Not Found - Run Data Prep First')
        except Exception, e:
            tb = sys.exc_info()[2]
            arcpy.AddMessage("Line %i" % tb.tb_lineno)
            arcpy.AddMessage(e.message)
        return

class SEGID(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "6. SEGID Check"
        self.description = "The tool used to compare SEGIDs to ensure they are splitting at the proper junctions"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Input Workspace",
            name="in_ws",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")
        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        try:
            ws = str(parameters[0].value)
            arcpy.AddMessage(ws)

            arcpy.env.overwriteOutput = True
            arcpy.env.XYTolerance = "0.0001 Meters"

            today = str(date.today())
            day = today.replace('-', '')

            datechk = arcpy.Exists(ws + os.sep + 'Data_' + day)
            if datechk is True:
                arcpy.AddMessage('Data Folder Found - Processing Will Begin')
                junctions = 'junctions_lyr'
                roads_lyr = 'roads_lyr'
                dw_lyr = 'dw_lyr'


                #ADD SEGID 0 CHECK

                arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'Junctionsextracted_' + day, 'juncs', 'JUNCTYPE = 1')

                arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day, dw_lyr, "ROADCLASS LIKE 'DW'")

                arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'NSRNextracted_' + day, 'tmp_roads', "ROADCLASS NOT LIKE 'DW'")

                arcpy.SelectLayerByLocation_management('juncs', 'INTERSECT', dw_lyr)


                arcpy.SelectLayerByLocation_management('juncs', 'INTERSECT', 'tmp_roads', selection_type='REMOVE_FROM_SELECTION')

                arcpy.CalculateField_management('juncs', 'ErrorType', "'SEGID 0'", "PYTHON_9.3")





                arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'Junctionsextracted_' + day, junctions, "ErrorType IS NULL AND JUNCTYPE = 1")
                arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data_' + day + os.sep + 'NSRNDissolved_' + day, roads_lyr)



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
                                matching = [s for s in chklist if jxy in s]
                                if len(chklist) > len(matching):
                                    arcpy.SelectLayerByAttribute_management(junctions, 'NEW_SELECTION', "JUNCTIONID = " + str(srow[0]))
                                    arcpy.SelectLayerByLocation_management(dw_lyr, 'INTERSECT', junctions, selection_type='NEW_SELECTION')
                                    dw_chk = int(arcpy.GetCount_management(dw_lyr).getOutput(0))
                                    if dw_chk == 1:
                                        arcpy.AddMessage( 'Dry Weather Intersection')
                                        with arcpy.da.UpdateCursor(junctions, ['ErrorType']) as DWcur:
                                            for DWrow in DWcur:
                                                DWrow[0] = 'DW Intersection'
                                                DWcur.updateRow(DWrow)
                                    else:
                                        arcpy.AddMessage( 'Possible Error')
                                        with arcpy.da.UpdateCursor(junctions, ['ErrorType']) as ucur:
                                            for urow in ucur:
                                                urow[0] = 'Investigate'
                                                ucur.updateRow(urow)
                            else:
                                arcpy.AddMessage('No road selected')
                            arcpy.AddMessage('###   Finished Point   ###\n')
                            arcpy.SelectLayerByAttribute_management(junctions, 'CLEAR_SELECTION')
                            arcpy.SelectLayerByAttribute_management(roads_lyr, 'CLEAR_SELECTION')


            else:
                arcpy.AddMessage('Data Folder Not Found - Run Data Prep First')





        except Exception, e:
            tb = sys.exc_info()[2]
            arcpy.AddMessage("Line %i" % tb.tb_lineno)
            arcpy.AddMessage(e.message)

        return




