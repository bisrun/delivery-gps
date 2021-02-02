import os
import pandas as pd
import numpy as np
import geopandas as gpd
#from shapely.geometry import Point
from nvconfig import nvconfig
from nvlogger import Logger
from gpslog_files import LogFileList
from gpslog_files import GpsShpCtl
import nvcommon


def run(step):
    try:

        cc = nvconfig.instance()
        cc.setInit("")
        ret = cc.load_file()
        if ret < 0 :
            return -1

        nvcommon.createFolder(cc._SELECTED_GPS_DIR_PATH)

        logManager = Logger.instance()
        logManager.setLogger(cc._LOG_FILE_PATH)
        logger = logManager.getLogger()
        logger.debug("debug test")

        my_step = 1
        if  step <= my_step  :
            logger.debug("-step 1 -")

        my_step = 2
        if  step <= my_step  :
            logger.debug("-step 2 -")


        my_step = 3
        if  step <= my_step  :
            logger.debug("-step 3 -")
            gps_path_list = LogFileList(cc._GPSLOG_FILE_PATH)
            gps_path_list.loadFilePath()

            flist = GpsShpCtl(gps_path_list.logFilePath)
            flist.IsDeliverer()

    except KeyboardInterrupt:
        print('\n\rquit')

if __name__ == '__main__':
    run(3)