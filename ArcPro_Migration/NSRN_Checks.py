from datetime import *

import arcpy
import os
import shutil
import traceback


class Var(object):
    # ws = r'\\geostor2.gov.ns.ca\SHR-NSGC\NSCAF\Users\ChrisHarlow\Projects\NSRN_Checks\Databases'
    # ws = r'N:\Users\ChrisHarlow\Projects\NSRN_Checks\Databases'
    ws = r'D:'
    sws = ws + os.sep + 'scratch.gdb'
    db = r'C:\Users\harlowcn\AppData\Roaming\Esri\ArcGISPro\Favorites\ORCL1.sde'
    day = str(date.today()).replace('-', '')
    gdb = ws + os.sep + day + '.gdb'
    XYTolerance = '0.0001 Meters'


def printmsg():
    print('Workspace:         ' + Var.ws)
    print('Scratch Workspace: ' + Var.sws.rsplit(os.sep, 1)[1])
    print('Oracle Database:   ' + Var.db.rsplit(os.sep, 1)[1])
    print('Day:               ' + Var.day)
    print('Geodatabase:       ' + Var.gdb.rsplit(os.sep, 1)[1])
    print('XY Tolerance:      ' + Var.XYTolerance + '\n\n')
    return


def main():
    import arcpy
    mstart_time = datetime.datetime.now()

    print('Creating Scratch Workspace')
    schk = arcpy.Exists(Var.sws)
    if schk is False:
        print('Scratch Workspace Created\n')
        arcpy.CreateFileGDB_management(Var.ws,'Scratch')

    print('###################################################################')
    print('###                     Starting Data Prep                      ###')
    start_time = datetime.datetime.now()
    import DataPrep
    end_time = datetime.datetime.now()
    elt = end_time - start_time
    print('Start Time:   ' + str(start_time))
    print('End Time:     ' + str(end_time))
    print('Elapsed Time: ' + str(elt))
    print('###                     Data Prep Complete                      ###')
    print('###################################################################\n')

    gdbchk = arcpy.Exists(Var.gdb)
    if gdbchk is False:
        print('### ' + Var.day + ' File Geodatabase cannot be found - Process ABORTED ###\n')
    else:
        tchk = arcpy.Exists(Var.gdb + os.sep + 'Data' + os.sep + 'Topology_point')
        if tchk is False:
            print('There Are No Topology Points - Skipping Pseudo Nodes and Dangles Tools')
        else:
            print('###################################################################')
            print('###                    Starting Pseudo Nodes                    ###')
            start_time = datetime.datetime.now()
            import PseudoNodes
            end_time = datetime.datetime.now()
            elt = end_time - start_time
            print('Start Time:   ' + str(start_time))
            print('End Time:     ' + str(end_time))
            print('Elapsed Time: ' + str(elt))
            print('###                    Pseudo Nodes Complete                    ###')
            print('###################################################################\n')

            print('###################################################################')
            print('###                      Starting Dangles                       ###')
            start_time = datetime.datetime.now()
            import Dangles
            end_time = datetime.datetime.now()
            elt = end_time - start_time
            print('Start Time:   ' + str(start_time))
            print('End Time:     ' + str(end_time))
            print('Elapsed Time: ' + str(elt))
            print('###                      Dangles Complete                       ###')
            print('###################################################################\n')
        print('###################################################################')
        print('###                  Starting Dissolved SEGID                   ###')
        start_time = datetime.datetime.now()
        import DissolvedSEGID
        end_time = datetime.datetime.now()
        elt = end_time - start_time
        print('Start Time:   ' + str(start_time))
        print('End Time:     ' + str(end_time))
        print('Elapsed Time: ' + str(elt))
        print('###                   Dissolved SEGID Complete                  ###')
        print('###################################################################\n')

        print('###################################################################')
        print('###                       Starting SEGID                        ###')
        start_time = datetime.datetime.now()
        import SEGID
        end_time = datetime.datetime.now()
        elt = end_time - start_time
        print('Start Time:   ' + str(start_time))
        print('End Time:     ' + str(end_time))
        print('Elapsed Time: ' + str(elt))
        print('###                        SEGID Complete                       ###')
        print('###################################################################\n')

        print('###################################################################')
        print('###                        Starting LRS                         ###')
        start_time = datetime.datetime.now()
        import LRS
        end_time = datetime.datetime.now()
        elt = end_time - start_time
        print('Start Time:   ' + str(start_time))
        print('End Time:     ' + str(end_time))
        print('Elapsed Time: ' + str(elt))
        print('###                         LRS Complete                        ###')
        print('###################################################################\n')

        print('###################################################################')
        print('###                   Starting Small Segments                   ###')
        start_time = datetime.datetime.now()
        import SmallSegments
        end_time = datetime.datetime.now()
        elt = end_time - start_time
        print('Start Time:   ' + str(start_time))
        print('End Time:     ' + str(end_time))
        print('Elapsed Time: ' + str(elt))
        print('###                    Small Segments Complete                  ###')
        print('###################################################################\n')

        # del arcpy
        #
        # shutil.rmtree(Var.sws, ignore_errors=True)

        mend_time = datetime.datetime.now()
        melt = mend_time - mstart_time
        print('Start Time:   ' + str(mstart_time))
        print('End Time:     ' + str(mend_time))
        print('Elapsed Time: ' + str(melt))
        return


if __name__ == '__main__':
    try:
        status = arcpy.SetProduct('arcInfo')
        if status == 'CheckedOut':
            print('\n\n\nArcInfo Checked Out - Tools Can Be Run\n\n\n')
            printmsg()
            main()
        if status == 'AlreadyInitialized':
            print('\n\n\nArcInfo Already Initialized - Tools Can Be Run\n\n\n')
            printmsg()
            main()
        if status == 'NotLicensed':
            print('\n\n\nArcInfo Not Licensed - Please Contact Your Systems Administrator')
            print('Process Aborting\n\n\n')
        if status == 'Failed':
            print('\n\n\nArcInfo Licensing Failed - Please Contact Your Systems Administrator')
            print('Process Aborting\n\n\n')
            print(traceback.format_exc())
    except:
        print('Something Went Wrong...')
        print(traceback.format_exc())
