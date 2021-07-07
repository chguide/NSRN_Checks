import arcpy, os, sys
from arcpy import *
from datetime import *
from time import *
start_time = datetime.now()
try:
    arcpy.env.overwriteOutput = True
    ws = r"D:\Work\PseudoNodes\Nodes_June2018.gdb"
    arcpy.env.workspace = ws
    errorpts = ws + os.sep + 'TopologyErrors' + os.sep + 'Data_Topology_point'
    print errorpts
    if int(arcpy.GetCount_management(errorpts).getOutput(0)) > 0:
        roads_lyr = "nscaf_roads"
        errorpts_lyr = 'errorpts_lyr'
        arcpy.MakeFeatureLayer_management(ws + os.sep + 'Data' + os.sep + 'NSRN',roads_lyr)
        arcpy.MakeFeatureLayer_management(errorpts, errorpts_lyr)
        scur = arcpy.SearchCursor(errorpts_lyr)
        for row in scur:
            sfeat1 = row.getValue("OriginObjectID")
            sfeat2 = row.getValue("DestinationObjectID")
            print "Origin ObjectID:      " + str(sfeat1)
            print "Destination ObjectID: " + str(sfeat2)
            arcpy.SelectLayerByAttribute_management(roads_lyr,'NEW_SELECTION', "OBJECTID = " + str(sfeat1) + " OR OBJECTID = " + str(sfeat2) + " ")
            roadcur = arcpy.SearchCursor(roads_lyr)
            chklist = []
            for rdrow in roadcur:
                rd1 = rdrow.getValue('MUN_ID')
                chklist.append(str(rd1))
                print "MUN_ID: " + str(rd1)
            if chklist[0] == chklist[1]:
                print 'Values match - possible error'
                print ''
            else:
                print 'Values are different - false error'
                print ''
                arcpy.SelectLayerByAttribute_management(errorpts_lyr,'NEW_SELECTION', "OriginObjectID = " + str(sfeat1) + " OR DestinationObjectID = " + str(sfeat2) + " ")
                arcpy.Append_management(errorpts_lyr, ws + os.sep + 'FalseErrors' + os.sep + 'MUNID_Change', 'NO_TEST')
                arcpy.SelectLayerByAttribute_management(errorpts_lyr,'CLEAR_SELECTION')
                arcpy.SelectLayerByAttribute_management(roads_lyr,'CLEAR_SELECTION')
    else:
        print 'There are no features to examine'
    del row, scur,errorpts_lyr, roads_lyr, rdrow, roadcur
except Exception, e:
    tb = sys.exc_info()[2]
    print "Line %i" % tb.tb_lineno
    print e.message
end_time = datetime.now()
elt = end_time - start_time

print "Start Time: ", start_time
print "End Time: ", end_time
print "Elapsed Time: ", elt
print "Script complete.\n"