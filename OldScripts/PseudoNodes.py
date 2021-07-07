import arcpy, os, sys
from arcpy import *
from datetime import *
from time import *
start_time = datetime.now()
try:
    env.overwriteOutput = True
    ws = r"D:\Work\PseudoNodes\Nodes_June2018.gdb"
    env.workspace = ws
    errorpts = ws + os.sep + 'TopologyErrors' + os.sep + 'Data_Topology_point'
    print errorpts
    if int(arcpy.GetCount_management(errorpts).getOutput(0)) > 0:
        roads_lyr = 'nscaf_roads'
        errorpts_lyr = 'errorpts_lyr'
        MakeFeatureLayer_management(ws + os.sep + 'Data' + os.sep + 'NSRN',roads_lyr)
        MakeFeatureLayer_management(errorpts, errorpts_lyr)
        scur = SearchCursor(errorpts_lyr)
        for row in scur:
            sfeat1 = row.getValue("OriginObjectID")
            sfeat2 = row.getValue("DestinationObjectID")
            print "Origin ObjectID:      " + str(sfeat1)
            print "Destination ObjectID: " + str(sfeat2)
            SelectLayerByAttribute_management(roads_lyr,'NEW_SELECTION', "OBJECTID = " + str(sfeat1) + " OR OBJECTID = " + str(sfeat2) + " ")
            roadcur = SearchCursor(roads_lyr)
            chklist = []
            for rdrow in roadcur:
                rd1 = rdrow.getValue('Owner_Added')
                chklist.append(str(rd1))
                print "Owner_Added: " + str(rd1)
            if chklist[0] == chklist[1]:
                print 'Values match - possible error'
                print ''
            else:
                print 'Values are different - false error'
                print ''
                SelectLayerByAttribute_management(errorpts_lyr,'NEW_SELECTION', "OriginObjectID = " + str(sfeat1) + " OR DestinationObjectID = " + str(sfeat2) + " ")
                Append_management(errorpts_lyr, ws + os.sep + 'FalseErrors' + os.sep + 'Owner_Change', 'NO_TEST')
        SelectLayerByAttribute_management(errorpts_lyr,'CLEAR_SELECTION')
        SelectLayerByAttribute_management(roads_lyr,'CLEAR_SELECTION')
##        SelectLayerByLocation_management(errorpts_lyr, 'ARE_IDENTICAL_TO', ws + os.sep + 'FalseErrors' + os.sep + 'Owner_Change')
##        DeleteFeatures_management (errorpts_lyr)



        del row, scur,errorpts_lyr, roads_lyr, rdrow, roadcur
    else:
        print 'There are no features to examine'


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