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


    def fcimport(fc, name, query):
        arcpy.FeatureClassToFeatureClass_conversion(Var.db + os.sep + fc, Var.gdb + os.sep + 'Data', name, query)
        print(name + ' Feature Class Imported')
        return


    def tbimport(fc, name):
        arcpy.TableToTable_conversion(Var.db + os.sep + fc, Var.sws, name)
        # arcpy.MakeTableView_management(Var.sws + os.sep + name, name, "RETIRED LIKE \'N\'", workspace=Var.ws)
        # arcpy.SelectLayerByAttribute(name, where_clause="RETIRED LIKE 'N'")
        arcpy.TableToTable_conversion(Var.db + os.sep + fc, Var.gdb, name, "RETIRED LIKE 'N'")
        print(name + ' Table Imported')
        return


    def fadd(fc):
        arcpy.AddField_management(Var.gdb + os.sep + fc, 'ErrorType', 'TEXT')
        print(fc + ' Error Type Field Added')
        return


    def addindex(fc, fields, name):
        arcpy.AddIndex_management(Var.gdb + os.sep + fc, fields, name)
        print(fc + ' Indexes Added')
        return


    def rule(rule):
        arcpy.AddRuleToTopology_management(Var.gdb + os.sep + 'Data/Topology', rule, Var.gdb + os.sep + 'Data/NSRN')
        print(rule + ' Added To The Topology')
        return


    def cntchk(fc):
        if int(arcpy.GetCount_management(Var.gdb + os.sep + 'Data/Topology_' + fc).getOutput(0)) > 0:
            print('Topology_' + fc + ' Has Errors - Please Check')
        else:
            arcpy.Delete_management(Var.gdb + os.sep + 'Data/Topology_' + fc)
            print('Unused Topology_' + fc + ' Feature Class Removed')
        return

    gdbchk = arcpy.Exists(Var.gdb)
    if gdbchk is True:
        print(str(Var.day) + ' DB Already Exists - Please Use That Data\n')
    else:
        arcpy.CreateFileGDB_management(Var.ws, Var.day)
        print(Var.day + ' File Geodatabase Created')
        arcpy.CreateFeatureDataset_management(Var.gdb, 'Data', 'NAD 1983 CSRS UTM Zone 20N')
        print('Feature Dataset Created\n')

        fcimport('NSCAF.NSCAF' + os.sep + 'NSCAF.nscaf_gsa', 'GSA', "RETIRED LIKE 'N'")
        # fcimport('NSRN.NSRN' + os.sep + 'NSRN.blkpassage', 'BlockedPassages', "RETIRED LIKE 'N'")
        fcimport('NSRN.NSRN' + os.sep + 'NSRN.junctions', 'Junctions', "RETIRED LIKE 'N'")
        fcimport('NSRN.NSRN' + os.sep + 'NSRN.nsrn', 'NSRN', "RETIRED LIKE 'N' AND IDS > 0")
        print('')

        tbimport('NSCAF.SEG_TAB', 'SEGTAB')
        tbimport('NSRN.LRS', 'LRS')
        print('')

        addindex('Data' + os.sep + 'Junctions', ['JUNCTYPE', 'JUNCTIONID'], 'Junctions')
        addindex('Data' + os.sep + 'NSRN', ['SEGID', 'ROADCLASS', 'MUNID', 'STREET'], 'NSRN')
        addindex('SEGTAB', ['SEGID', 'OWNER'], 'SEGTAB')
        addindex('LRS', ['ROADSEGID', 'IDS', 'START_DIST', 'STOP_DIST'], 'LRS')
        print('')

        arcpy.MakeFeatureLayer_management(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'NSRN_lyr')
        print('NSRN_lyr Created')
        arcpy.MakeTableView_management(Var.gdb + os.sep + 'SEGTAB', 'SEGTAB_view')
        print('SEGTAB_view Created\n')

        fadd('Data' + os.sep + 'Junctions')
        fadd('LRS')
        fadd('Data' + os.sep + 'NSRN')
        arcpy.JoinField_management('NSRN_lyr', 'SEGID', 'SEGTAB_view', 'SEGID', ['OWNER'])
        print('Owner Field Added to the NSRN\n')

        addindex('Data' + os.sep + 'NSRN', ['OWNER'], 'NSRN_OWNER')
        print('')

        arcpy.CreateTopology_management(Var.gdb + os.sep + 'Data', 'Topology', float(Var.XYTolerance.strip('Metres')))
        print('Topology Created')
        arcpy.AddFeatureClassToTopology_management(Var.gdb + os.sep + 'Data/Topology', Var.gdb + os.sep + 'Data/NSRN', 1, 1)
        print('NSRN Added To The Topology')
        rule('Must Not Have Pseudo-Nodes (Line)')
        rule('Must Not Have Dangles (Line)')
        arcpy.ValidateTopology_management(Var.gdb + os.sep + 'Data/Topology')
        print('Topology Validated')
        arcpy.ExportTopologyErrors_management(Var.gdb + os.sep + 'Data/Topology', Var.gdb + os.sep + 'Data', 'Topology')
        print('Topological Errors Exported')
        cntchk('point')
        cntchk('line')
        cntchk('poly')
        print('')

        fadd('Data' + os.sep + 'Topology_point')

        arcpy.Compact_management(Var.gdb)
        print(str(Var.day) + ' DB Compacted\n')

except:
    print('Something Went Wrong...')
    print(traceback.format_exc())
    sys.exit()

del arcpy
