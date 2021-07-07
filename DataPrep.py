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


    def fcimport(fc, name, query):
        arcpy.FeatureClassToFeatureClass_conversion(Var.db + os.sep + fc, Var.gdb + os.sep + 'Data', name, query)
        logfile.info(name + ' Feature Class Imported')
        return


    def tbimport(fc, name):
        arcpy.MakeTableView_management(Var.db + os.sep + fc, name, "RETIRED LIKE 'N'", Var.ws)
        arcpy.TableToTable_conversion(name, Var.gdb, name)
        logfile.info(name + ' Table Imported')
        return


    def fadd(fc):
        arcpy.AddField_management(Var.gdb + os.sep + fc, 'ErrorType', 'TEXT')
        logfile.info(fc + ' Error Type Field Added')
        return


    def addindex(fc, fields, name):
        arcpy.AddIndex_management(Var.gdb + os.sep + fc, fields, name)
        logfile.info(fc + ' Indexes Added')
        return


    def rule(rule):
        arcpy.AddRuleToTopology_management(Var.gdb + os.sep + 'Data/Topology', rule, Var.gdb + os.sep + 'Data/NSRN')
        logfile.info(rule + ' Added To The Topology')
        return


    def cntchk(fc):
        if int(arcpy.GetCount_management(Var.gdb + os.sep + 'Data/Topology_' + fc).getOutput(0)) > 0:
            logfile.info('Topology_' + fc + ' Has Errors - Please Check')
        else:
            arcpy.Delete_management(Var.gdb + os.sep + 'Data/Topology_' + fc)
            logfile.info('Unused Topology_' + fc + ' Feature Class Removed')
        return

    gdbchk = arcpy.Exists(Var.gdb)
    if gdbchk is True:
        logfile.warning(str(Var.day) + ' DB Already Exists - Please Use That Data\n')
    else:
        arcpy.CreateFileGDB_management(Var.ws, Var.day)
        logfile.info(Var.day + ' File Geodatabase Created')
        arcpy.CreateFeatureDataset_management(Var.gdb, 'Data', 'NAD 1983 CSRS UTM Zone 20N')
        logfile.info('Feature Dataset Created\n')

        fcimport('NSCAF.NSCAF\NSCAF.nscaf_gsa', 'GSA', "RETIRED LIKE 'N'")
        fcimport('NSRN.NSRN\NSRN.blkpassage', 'BlockedPassages', "RETIRED LIKE 'N'")
        fcimport('NSRN.NSRN\NSRN.junctions', 'Junctions', "RETIRED LIKE 'N'")
        fcimport('NSRN.NSRN\NSRN.nsrn', 'NSRN', "RETIRED LIKE 'N' AND IDS > 0")
        logfile.info('')

        tbimport('NSCAF.SEG_TAB', 'SEGTAB')
        tbimport('NSRN.LRS', 'LRS')
        logfile.info('')

        addindex('Data' + os.sep + 'Junctions', ['JUNCTYPE', 'JUNCTIONID'], 'Junctions')
        addindex('Data' + os.sep + 'NSRN', ['SEGID', 'ROADCLASS', 'MUNID', 'STREET'], 'NSRN')
        addindex('SEGTAB', ['SEGID', 'OWNER'], 'SEGTAB')
        addindex('LRS', ['ROADSEGID', 'IDS', 'START_DIST', 'STOP_DIST'], 'LRS')
        logfile.info('')

        arcpy.MakeFeatureLayer_management(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'NSRN_lyr')
        logfile.info('NSRN_lyr Created')
        arcpy.MakeTableView_management(Var.gdb + os.sep + 'SEGTAB', 'SEGTAB_view')
        logfile.info('SEGTAB_view Created\n')

        fadd('Data' + os.sep + 'Junctions')
        fadd('LRS')
        fadd('Data' + os.sep + 'NSRN')
        arcpy.JoinField_management('NSRN_lyr', 'SEGID', 'SEGTAB_view', 'SEGID', ['OWNER'])
        logfile.info('Owner Field Added to the NSRN\n')

        addindex('Data' + os.sep + 'NSRN', ['OWNER'], 'NSRN_OWNER')
        logfile.info('')

        arcpy.CreateTopology_management(Var.gdb + os.sep + 'Data', 'Topology', float(Var.XYTolerance.strip('Metres')))
        logfile.info('Topology Created')
        arcpy.AddFeatureClassToTopology_management(Var.gdb + os.sep + 'Data/Topology', Var.gdb + os.sep + 'Data/NSRN', 1, 1)
        logfile.info('NSRN Added To The Topology')
        rule('Must Not Have Pseudo-Nodes (Line)')
        rule('Must Not Have Dangles (Line)')
        arcpy.ValidateTopology_management(Var.gdb + os.sep + 'Data/Topology')
        logfile.info('Topology Validated')
        arcpy.ExportTopologyErrors_management(Var.gdb + os.sep + 'Data/Topology', Var.gdb + os.sep + 'Data', 'Topology')
        logfile.info('Topological Errors Exported')
        cntchk('point')
        cntchk('line')
        cntchk('poly')
        logfile.info('')

        fadd('Data' + os.sep + 'Topology_point')

        arcpy.Compact_management(Var.gdb)
        logfile.info(str(Var.day) + ' DB Compacted\n')

except:
    logfile.critical('Something Went Wrong...')
    logfile.critical(traceback.format_exc())
    sys.exit()

del arcpy


