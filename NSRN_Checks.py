import arcpy, os, sys, logging, traceback
from datetime import *


class Var(object):
    # pfolder = r'C:\Users\harlowcn\Work\NSRN_Checks'
    pfolder = r'N:\Users\ChrisHarlow\Projects\NSRN_Checks'
    # pfolder = r'D:\NSRN_Checks'
    ws = pfolder + os.sep + 'Databases'
    sws = ws + os.sep + 'scratch.gdb'
    db = r'Database Connections\orcl1.sde'
    nsgi = r'GIS Servers\arcgis on nsgiwa.novascotia.ca (user)'
    logfolder = pfolder + os.sep + 'LogFiles'
    day = str(date.today()).replace('-', '')
    gdb = ws + os.sep + day + '.gdb'
    XYTolerance = '0.0001 Meters'


def logger(name):
    log = logging.Logger(name)
    if not log.handlers:
        log.propagate = 0
        fh = logging.FileHandler(Var.logfolder + os.sep + Var.day + '_Log.txt')
        sh = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)-8s %(message)s', '%H:%M')
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)
        log.addHandler(fh)
        log.addHandler(sh)
        log.setLevel(logging.INFO)
    return log


def printmsg():
    logfile.info('Project Folder:         ' + Var.pfolder)
    logfile.info('Log Folder:                                                      ' + os.sep + Var.logfolder.rsplit(os.sep, 1)[1])
    logfile.info('Workspace:                                                       ' + os.sep + Var.ws.rsplit(os.sep, 1)[1])
    logfile.info('Geodatabase:                                                               ' + os.sep + Var.gdb.rsplit(os.sep, 1)[1])
    logfile.info('Scratch Workspace:                                                         ' + os.sep + Var.sws.rsplit(os.sep, 1)[1])
    logfile.info('Oracle Database:        ' + Var.db.rsplit(os.sep, 1)[1])
    logfile.info('NSGI:                   ' + Var.nsgi)
    logfile.info('Day:                    ' + Var.day)
    logfile.info('XY Tolerance:           ' + Var.XYTolerance + '\n\n')
    return


def main():
    import arcpy
    mstart_time = datetime.now()

    schk = arcpy.Exists(Var.sws)
    if schk is False:
        logfile.info('Scratch Workspace Created\n')
        arcpy.CreateFileGDB_management(Var.ws, 'Scratch')

    logfile.info('###################################################################')
    logfile.info('###                     Starting Data Prep                      ###')
    start_time = datetime.now()
    import DataPrep
    end_time = datetime.now()
    elt = end_time - start_time
    logfile.info('Start Time:   ' + str(start_time))
    logfile.info('End Time:     ' + str(end_time))
    logfile.info('Elapsed Time: ' + str(elt))
    logfile.info('###                     Data Prep Complete                      ###')
    logfile.info('###################################################################\n')

    gdbchk = arcpy.Exists(Var.gdb)
    if gdbchk is False:
        logfile.error('### ' + Var.day + ' File Geodatabase cannot be found - Process ABORTED ###\n')
    else:
        tchk = arcpy.Exists(Var.gdb + os.sep + 'Data' + os.sep + 'Topology_point')
        if tchk is False:
            logfile.warning('There Are No Topology Points - Skipping Pseudo Nodes and Dangles Tools')
        else:
            logfile.info('###################################################################')
            logfile.info('###                    Starting Pseudo Nodes                    ###')
            start_time = datetime.now()
            import PseudoNodes
            end_time = datetime.now()
            elt = end_time - start_time
            logfile.info('Start Time:   ' + str(start_time))
            logfile.info('End Time:     ' + str(end_time))
            logfile.info('Elapsed Time: ' + str(elt))
            logfile.info('###                    Pseudo Nodes Complete                    ###')
            logfile.info('###################################################################\n')

            logfile.info('###################################################################')
            logfile.info('###                      Starting Dangles                       ###')
            start_time = datetime.now()
            import Dangles
            end_time = datetime.now()
            elt = end_time - start_time
            logfile.info('Start Time:   ' + str(start_time))
            logfile.info('End Time:     ' + str(end_time))
            logfile.info('Elapsed Time: ' + str(elt))
            logfile.info('###                      Dangles Complete                       ###')
            logfile.info('###################################################################\n')
        logfile.info('###################################################################')
        logfile.info('###                  Starting Dissolved SEGID                   ###')
        start_time = datetime.now()
        import DissolvedSEGID
        end_time = datetime.now()
        elt = end_time - start_time
        logfile.info('Start Time:   ' + str(start_time))
        logfile.info('End Time:     ' + str(end_time))
        logfile.info('Elapsed Time: ' + str(elt))
        logfile.info('###                   Dissolved SEGID Complete                  ###')
        logfile.info('###################################################################\n')

        logfile.info('###################################################################')
        logfile.info('###                       Starting SEGID                        ###')
        start_time = datetime.now()
        import SEGID
        end_time = datetime.now()
        elt = end_time - start_time
        logfile.info('Start Time:   ' + str(start_time))
        logfile.info('End Time:     ' + str(end_time))
        logfile.info('Elapsed Time: ' + str(elt))
        logfile.info('###                        SEGID Complete                       ###')
        logfile.info('###################################################################\n')

        logfile.info('###################################################################')
        logfile.info('###                        Starting LRS                         ###')
        start_time = datetime.now()
        import LRS
        end_time = datetime.now()
        elt = end_time - start_time
        logfile.info('Start Time:   ' + str(start_time))
        logfile.info('End Time:     ' + str(end_time))
        logfile.info('Elapsed Time: ' + str(elt))
        logfile.info('###                         LRS Complete                        ###')
        logfile.info('###################################################################\n')

        logfile.info('###################################################################')
        logfile.info('###                   Starting Small Segments                   ###')
        start_time = datetime.now()
        import SmallSegments
        end_time = datetime.now()
        elt = end_time - start_time
        logfile.info('Start Time:   ' + str(start_time))
        logfile.info('End Time:     ' + str(end_time))
        logfile.info('Elapsed Time: ' + str(elt))
        logfile.info('###                    Small Segments Complete                  ###')
        logfile.info('###################################################################\n')

        logfile.info('###################################################################')
        logfile.info('###                   Starting Comparison                       ###')
        start_time = datetime.now()
        import Comparison
        end_time = datetime.now()
        elt = end_time - start_time
        logfile.info('Start Time:   ' + str(start_time))
        logfile.info('End Time:     ' + str(end_time))
        logfile.info('Elapsed Time: ' + str(elt))
        logfile.info('###                     Comparison Complete                     ###')
        logfile.info('###################################################################\n')

        logfile.info('###################################################################')
        logfile.info('###                     Starting Setup                          ###')
        start_time = datetime.now()
        import Setup
        end_time = datetime.now()
        elt = end_time - start_time
        logfile.info('Start Time:   ' + str(start_time))
        logfile.info('End Time:     ' + str(end_time))
        logfile.info('Elapsed Time: ' + str(elt))
        logfile.info('###                        Setup Complete                       ###')
        logfile.info('###################################################################\n')

        mend_time = datetime.now()
        melt = mend_time - mstart_time
        logfile.info('Start Time:   ' + str(mstart_time))
        logfile.info('End Time:     ' + str(mend_time))
        logfile.info('Elapsed Time: ' + str(melt))
        return


if __name__ == '__main__':
    logfile = logger(__name__)
    try:
        status = arcpy.SetProduct('arcInfo')
        if status == 'CheckedOut':
            logfile.info('\n\n\nArcInfo Checked Out - Tools Can Be Run\n\n\n')
            printmsg()
            main()
        elif status == 'AlreadyInitialized':
            logfile.info('\n\n\nArcInfo Already Initialized - Tools Can Be Run\n\n\n')
            printmsg()
            main()
        elif status == 'NotLicensed':
            logfile.critical('\n\n\nArcInfo Not Licensed - Please Contact Your Systems Administrator')
            logfile.critical('Process Aborting\n\n\n')
        elif status == 'Failed':
            logfile.critical('\n\n\nArcInfo Licensing Failed - Please Contact Your Systems Administrator')
            logfile.critical('Process Aborting\n\n\n')
            tb = sys.exc_info()[2]
            logfile.critical("Line %i" % tb.tb_lineno)
            logfile.critical(Exception.message)
    except:
        logfile.critical('Something Went Wrong...')
        logfile.critical(traceback.format_exc())
        sys.exit()
