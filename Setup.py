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


    def addlyr(feature, dname, query=None):
        valchk = arcpy.Exists(feature)
        if valchk == False:
            logfile.error(feature.rsplit(os.sep, 1)[1] + ' Does Not Exist - Skipping')
        else:
            arcpy.MakeFeatureLayer_management(feature,'seltest', query)
            cntchk = int(arcpy.GetCount_management('seltest')[0])
            if cntchk == 0:
                logfile.error(dname + ' Does Not Have Content - Skipping')
                for lyr in arcpy.mapping.ListLayers(mxd, dname):
                    if lyr.isBroken:
                        arcpy.mapping.RemoveLayer(df, lyr)
                        logfile.info(dname + ' Being Removed From MXD')
            else:
                for lyr in arcpy.mapping.ListLayers(mxd, dname):
                    if lyr.name == dname:
                        lyr.replaceDataSource(Var.gdb, 'FILEGDB_WORKSPACE', feature.rsplit(os.sep, 1)[1])
                        logfile.info(feature.rsplit(os.sep, 1)[1] + ' Added To The MXD')
                arcpy.Delete_management('setltest')
        return


    def addtbl(tblname, query):
        tbl_chk = arcpy.Exists(tblname)
        if tbl_chk is False:
            logfile.error(tblname.rsplit(os.sep, 1)[1] + ' Does Not Exist')
        else:
            arcpy.MakeTableView_management(tblname, 'tbl_view', query)
            fchk = int(arcpy.GetCount_management('tbl_view')[0])
            if fchk == 0:
                logfile.warning(tblname.rsplit(os.sep, 1)[1] + ' Does Not Have Any Records To Process\n')
            else:
                tbl = arcpy.mapping.TableView(tblname)
                tbl.definitionQuery = query
                arcpy.mapping.AddTableView(df, tbl)
                logfile.info(tblname.rsplit(os.sep, 1)[1] + ' Added to the MXD')
                arcpy.Delete_management('tbl_view')
        return

    map_file = Var.ws[:-10] + os.sep + 'MXD' + os.sep + 'Template.mxd'
    mxd = arcpy.mapping.MapDocument(map_file)
    mxd.saveACopy(Var.ws[:-10] + os.sep + 'MXD' + os.sep + Var.day + '.mxd')
    del mxd

    map_file = Var.ws[:-10] + os.sep + 'MXD' + os.sep + Var.day + '.mxd'
    open(map_file, 'r').close()

    mxd = arcpy.mapping.MapDocument(map_file)
    df = arcpy.mapping.ListDataFrames(mxd)[0]

    addlyr(Var.gdb + os.sep + 'Data' + os.sep + 'GSA', 'GSA')
    addlyr(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'NSRN')
    addlyr(Var.gdb + os.sep + 'Data' + os.sep + 'NSRN', 'NSRN Errors', "ErrorType LIKE 'Investigate'")
    addlyr(Var.gdb + os.sep + 'Data' + os.sep + 'Junctions', 'Junctions')
    addlyr(Var.gdb + os.sep + 'Data' + os.sep + 'Topology_point', 'Topology Errors')
    logfile.info('')

    addtbl(Var.gdb + os.sep + 'MultipleSEGID', "ErrorType LIKE 'Investigate' OR ErrorType LIKE 'Fix'")
    addtbl(Var.gdb + os.sep + 'LRS', "ErrorType LIKE 'Investigate' OR ErrorType LIKE 'Fix'")
    logfile.info('')

    mxd.save()

    del mxd

    os.startfile(map_file)
    logfile.info('Opening MXD - ' + map_file.rsplit(os.sep, 1)[1] + '\n')

except:
    logfile.critical('Something Went Wrong...')
    logfile.critical(traceback.format_exc())
    sys.exit()

del arcpy

