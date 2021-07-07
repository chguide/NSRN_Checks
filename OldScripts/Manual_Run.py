ws = r"N:\Users\ChrisHarlow\Projects\PseudoNodes\PseudoNodes.gdb"
import arcpy, os, sys
import arcpy, os, sys
import arcpy, sys, os

from datetime import *

start_time = datetime.now()
ws = r"N:\Users\ChrisHarlow\Projects\PseudoNodes\PseudoNodes.gdb"
arcpy.env.overwriteOutput = True
arcpy.env.XYTolerance = "0.0001 Meters"

arcpy.env.workspace = ws

today = str(date.today())
day = today.replace('-', '')
sr = arcpy.SpatialReference('NAD 1983 CSRS UTM Zone 20N')
arcpy.CreateFeatureDataset_management(ws, 'PS_' + day, sr)


arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSCAF.NSCAF\NSCAF.nscaf_gsa', ws + os.sep + 'PS_' + day, 'GSA_' + day)
arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.blkpassage', ws + os.sep + 'PS_' + day, 'BlockedPassages_' + day)
arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.nsrn', ws + os.sep + 'PS_' + day, 'NSRN_' + day)

arcpy.TableToTable_conversion(r'Database Connections\orcl1.sde\NSCAF.SEG_TAB', ws, 'SEGTAB_' + day)

arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'GSA_' + day, ws + os.sep + 'PS_' + day + os.sep + 'GSAextracted_' + day, "RETIRED LIKE 'N'")
arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'BlockedPassages_' + day, ws + os.sep + 'PS_' + day + os.sep + 'BlockedPassagesextracted_' + day, "RETIRED LIKE 'N'")
arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'NSRN_' + day, ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, "RETIRED LIKE 'N' AND IDS > 0")

arcpy.TableSelect_analysis(ws + os.sep + 'SEGTAB_' + day, ws + os.sep + 'SEGTABextracted_' + day, "RETIRED LIKE 'N'")

arcpy.CreateTopology_management(ws + os.sep + 'PS_' + day, 'Topology_' + day, 0.001)
arcpy.AddFeatureClassToTopology_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day, ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, 1, 1)
arcpy.AddRuleToTopology_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day, 'Must Not Have Pseudo-Nodes (Line)', ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day)
arcpy.AddRuleToTopology_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day, 'Must Not Have Dangles (Line)', ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day)
arcpy.ValidateTopology_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day)
arcpy.ExportTopologyErrors_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day, ws + os.sep + 'PS_' + day, 'Topology_' + day)

arcpy.AddField_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', 'ErrorType', 'TEXT')

errorpts_lyr = 'errorpts_lyr'
arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', errorpts_lyr, "RuleDescription LIKE 'Must Not Have Pseudo Nodes'")
del errorpts_lyr
roads_lyr = 'roads_lyr'
arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr)


errorpts_lyr_dangles = 'errorpts_lyr_dangles'
arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', errorpts_lyr_dangles, "RuleDescription LIKE 'Must Not Have Dangles'")


roads_lyr_DW = 'roads_lyr2'
arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr_DW, "ROADCLASS = 'DW'")
arcpy.SelectLayerByLocation_management(errorpts_lyr_dangles, 'INTERSECT', roads_lyr_DW)
dw_chk = int(arcpy.GetCount_management(errorpts_lyr_dangles)[0])
if dw_chk == 0:
    arcpy.AddMessage('No Dry Weather Roads Match Any Topology Error Points')
else:
    arcpy.CalculateField_management(errorpts_lyr_dangles, 'ErrorType', "'Dry Weather'", 'PYTHON')
    
    arcpy.SelectLayerByAttribute_management(errorpts_lyr_dangles, 'CLEAR_SELECTION')
    arcpy.SelectLayerByAttribute_management(roads_lyr_DW, 'CLEAR_SELECTION')
    del roads_lyr_DW


arcpy.RefreshTOC()
arcpy.mapping.RemoveLayer('Layers', 'roads_lyr2')



roads_lyr_WA = 'roads_lyr3'
arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr_WA, "ROADCLASS = 'WA'")
arcpy.SelectLayerByLocation_management(errorpts_lyr_dangles, 'INTERSECT', roads_lyr_WA)
arcpy.CalculateField_management(errorpts_lyr_dangles, 'ErrorType', "'Water Access'", 'PYTHON')
arcpy.SelectLayerByAttribute_management(errorpts_lyr_dangles, 'CLEAR_SELECTION')
arcpy.SelectLayerByAttribute_management(roads_lyr_WA, 'CLEAR_SELECTION')
del roads_lyr_WA




errorpts_lyr_dangles_NULL = 'errorpts_lyr_dangles_NULL'
arcpy.arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', errorpts_lyr_dangles_NULL, "RuleDescription LIKE 'Must Not Have Dangles' AND ErrorType IS NULL")
buff_pts = 'in_memory\Point_Buffer'
arcpy.Buffer_analysis(errorpts_lyr_dangles_NULL, ws + os.sep + 'PS_' + day + os.sep + 'pt_buffer' + day, '5 Meters')
arcpy.SelectLayerByLocation_management(roads_lyr, 'INTERSECT', buff_pts)
arcpy.SelectLayerByLocation_management(roads_lyr, 'INTERSECT', errorpts_lyr_dangles_NULL, selection_type="REMOVE_FROM_SELECTION")
arcpy.SelectLayerByLocation_management(buff_pts, 'INTERSECT', roads_lyr, selection_type='NEW_SELECTION')
#arcpy.CopyFeatures_management("Point_Buffer", ws + os.sep + 'PS_' + day + os.sep + pt_buffer + day)
arcpy.CopyFeatures_management("Point_Buffer", ws + os.sep + 'PS_' + day + os.sep + 'pt_buffer' + day)
pt_buff_xport = 'pt_buffer20190031_lyr'
arcpy.MakeFeatureLayer_management("pt_buffer20190131", pt_buff_xport)
arcpy.SelectLayerByLocation_management(pt_buff_xport, 'INTERSECT', roads_lyr, selection_type='NEW_SELECTION')
arcpy.SelectLayerByLocation_management(errorpts_lyr_dangles_NULL, "WITHIN", buff_pts, selection_type='NEW_SELECTION', invert_spatial_relationship='INVERT')
arcpy.CalculateField_management(errorpts_lyr_dangles_NULL, 'ErrorType', 'Investigate', 'PYTHON')
arcpy.CalculateField_management(errorpts_lyr_dangles_NULL, 'ErrorType', "'Investigate'", 'PYTHON')



import arcpy, os, sys
roads_lyr_WA = 'roads_lyr3'
arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr_WA, "ROADCLASS = 'WA'")
arcpy.SelectLayerByLocation_management(errorpts_lyr_dangles, 'INTERSECT', roads_lyr_WA)
arcpy.CalculateField_management(errorpts_lyr_dangles, 'ErrorType', "'Water Access'", 'PYTHON')
arcpy.SelectLayerByAttribute_management(errorpts_lyr_dangles, 'CLEAR_SELECTION')
arcpy.SelectLayerByAttribute_management(roads_lyr_WA, 'CLEAR_SELECTION')
del roads_lyr_WA
errorpts_lyr_dangles_NULL = 'errorpts_lyr_dangles_NULL'
arcpy.arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'Topology_' + day + '_point', errorpts_lyr_dangles_NULL, "RuleDescription LIKE 'Must Not Have Dangles' AND ErrorType IS NULL")
buff_pts = 'in_memory\Point_Buffer'
arcpy.Buffer_analysis(errorpts_lyr_dangles_NULL, buff_pts, '5 Meters')
arcpy.SelectLayerByLocation_management(roads_lyr, 'INTERSECT', buff_pts)
arcpy.SelectLayerByLocation_management(roads_lyr, 'INTERSECT', errorpts_lyr_dangles_NULL, selection_type="REMOVE_FROM_SELECTION")
arcpy.SelectLayerByLocation_management(buff_pts, 'INTERSECT', roads_lyr, selection_type='NEW_SELECTION')
arcpy.CopyFeatures_management("Point_Buffer", ws + os.sep + 'PS_' + day + os.sep + 'pt_buffer' + day)
pt_buff_xport = 'pt_buffer_lyr'
arcpy.MakeFeatureLayer_management("pt_buffer20190131", pt_buff_xport)
arcpy.SelectLayerByLocation_management(pt_buff_xport, 'INTERSECT', roads_lyr, selection_type='NEW_SELECTION')
arcpy.SelectLayerByLocation_management(errorpts_lyr_dangles_NULL, "WITHIN", buff_pts, selection_type='NEW_SELECTION', invert_spatial_relationship='INVERT')
arcpy.CalculateField_management(errorpts_lyr_dangles_NULL, 'ErrorType', "'Valid'", 'PYTHON')



import arcpy, os, sys
arcpy.CopyFeatures_management("Point_Buffer", ws + os.sep + 'PS_' + day + os.sep + 'pt_buffer' + day)
pt_buff_xport = 'pt_buffer20190031_lyr'
arcpy.MakeFeatureLayer_management("pt_buffer20190131", pt_buff_xport)
arcpy.SelectLayerByLocation_management(pt_buff_xport, 'INTERSECT', roads_lyr, selection_type='NEW_SELECTION')
arcpy.SelectLayerByLocation_management(errorpts_lyr_dangles_NULL, "WITHIN", buff_pts, selection_type='NEW_SELECTION', invert_spatial_relationship='INVERT')
arcpy.CalculateField_management(errorpts_lyr_dangles_NULL, 'ErrorType', "'Valid'", 'PYTHON')



arcpy.SelectLayerByLocation_management(errorpts_lyr_dangles_NULL, "WITHIN", buff_pts, selection_type='NEW_SELECTION')

