import arcpy, os, sys
from datetime import *
start_time = datetime.now()
try:
    ws = r"N:\Users\ChrisHarlow\Projects\PseudoNodes\PseudoNodes.gdb"

    arcpy.env.overwriteOutput = True
    arcpy.env.XYTolerance = "0.0001 Meters"

    arcpy.env.workspace = ws
    today = str(date.today())
    day = today.replace('-', '')
    start_time = datetime.now()




    sr = arcpy.SpatialReference('NAD 1983 CSRS UTM Zone 20N')
    arcpy.CreateFeatureDataset_management(ws, 'PS_' + day, sr)
    arcpy.AddMessage(day + ' Feature Dataset Created')

    arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSCAF.NSCAF\NSCAF.nscaf_gsa', ws + os.sep + 'PS_' + day, 'GSA_' + day)
    arcpy.AddMessage('GSA Feature Class Imported')
    arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.blkpassage', ws + os.sep + 'PS_' + day, 'BlockedPassages_' + day)
    arcpy.AddMessage('Blocked Passages Feature Class Imported')
    arcpy.FeatureClassToFeatureClass_conversion(r'Database Connections\orcl1.sde\NSRN.NSRN\NSRN.nsrn', ws + os.sep + 'PS_' + day, 'NSRN_' + day)
    arcpy.AddMessage('NSRN Feature Classes Imported')

    arcpy.TableToTable_conversion(r'Database Connections\orcl1.sde\NSCAF.SEG_TAB', ws, 'SEGTAB_' + day)
    arcpy.AddMessage('SEG_TAB Table Imported')

    arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'GSA_' + day, ws + os.sep + 'PS_' + day + os.sep + 'GSAextracted_' + day, "RETIRED LIKE 'N'")
    arcpy.AddMessage('GSA Feature Class Selected')
    arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'BlockedPassages_' + day, ws + os.sep + 'PS_' + day + os.sep + 'BlockedPassagesextracted_' + day, "RETIRED LIKE 'N'")
    arcpy.AddMessage('Blocked Passages Feature Class Selected')
    arcpy.Select_analysis(ws + os.sep + 'PS_' + day + os.sep + 'NSRN_' + day, ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, "RETIRED LIKE 'N' AND IDS > 0")
    arcpy.AddMessage('NSRN Feature Class Selected')

    arcpy.TableSelect_analysis(ws + os.sep + 'SEGTAB_' + day, ws + os.sep + 'SEGTABextracted_' + day, "RETIRED LIKE 'N'")
    arcpy.AddMessage('SEG_TAB Table Selected')







    roads_lyr = 'roads'
    arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNextracted_' + day, roads_lyr, '"SEGID" <> 0')

    arcpy.Dissolve_management(roads_lyr, ws + os.sep + 'PS_' + day + os.sep + 'NSRNDissolved_' + day, "SEGID", multi_part="SINGLE_PART")
    del roads_lyr
    arcpy.AddIndex_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNDissolved_' + day, ['SEGID'], 'dissolved_' + day)

    roads_lyr = 'roads'
    arcpy.Statistics_analysis(ws + os.sep + 'PS_' + day + os.sep + 'NSRNDissolved_' + day, ws + os.sep + 'NSRNDissolvedStatistics_' + day, "SEGID COUNT", "SEGID")
    arcpy.AddIndex_management(ws + os.sep + 'NSRNDissolvedStatistics_' + day, ['SEGID'], 'dissolvedtable_' + day)
    arcpy.MakeFeatureLayer_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNDissolved_' + day, roads_lyr, )

    arcpy.AddJoin_management(roads_lyr, 'SEGID', ws + os.sep + 'NSRNDissolvedStatistics_' + day, 'SEGID')

    #arcpy.JoinField_management(ws + os.sep + 'PS_' + day + os.sep + 'NSRNDissolved_' + day, 'SEGID', ws + os.sep + 'NSRNDissolvedStatistics_' + day, 'SEGID', 'FREQUENCY')




except Exception, e:
    tb = sys.exc_info()[2]
    arcpy.AddMessage("Line %i" % tb.tb_lineno)
    arcpy.AddMessage(e.message)
del arcpy


end_time = datetime.now()
elt = end_time - start_time

print "Start Time: " + str(start_time)
print "End Time: " + str(end_time)
print "Elapsed Time: " + str(elt)
print "Script complete"