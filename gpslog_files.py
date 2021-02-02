import re
import glob
import geopandas as gpd
import math
from pyproj import Proj, Transformer
from datetime import datetime
import numpy as np
import pandas as pd
import os
import re
import shutil
from nvconfig import nvconfig

# file list를 관리한다.
class LogFileList :
    logFilePath = []
    logDirPath = ""
    def __init__(self, dir_pah):
        print("load file name {0}".format(dir_pah))
        self.setDirName(dir_pah)

    def setDirName(self, dir_path):
        self.logDirPath = dir_path

    def loadFilePath(self):
        #** --> recursive dir scan
        dir_filter = "{0}/**/*.shp".format(self.logDirPath)

        print(dir_filter)
        #for filename in glob.iglob(dir_filter , recursive=True):
        for filename in glob.glob(dir_filter, recursive=True):
            self.logFilePath.append(filename)
            #print(filename)
        self.logFilePath.sort()

    def printFilePath(self):
        i = 1
        for filename in  self.logFilePath :
            print( "{0} {1}".format( i, filename))
            i += 1

class LastUserInfo:
    x = 0  #utmk
    y = 0  #utmk
    ts = 0
    user_id = 0

    def __init__(self, x, y , ts, user_id):
        self.set_new_user(x, y , ts, user_id)

    def set_new_user(self, x, y , ts, user_id):
        self.x = x
        self.x = y
        self.x = ts
        self.user_id = user_id

    #user_id 다르면 .. return false
    #거리와 시간이 연결성 임계치 초과이면, 연결되어 있지 않다고 본다.

    def is_connected_prev_user(self, user_id, x, y, ts):
        if self.user_id != user_id :
            return False

        diff = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        if diff < 50:
            return False

        ts_diff = ts - self.ts
        if ts_diff < 300 or ts_diff > 1800 :
            return False

        return True


class GpsShpCtl:
    shpFileList = []
    user_dic={}
    transformer = Transformer.from_crs('epsg:4326', 'epsg:5178', always_xy=True)


    def __init__(self, shpFileList):
        self.shpFileList = shpFileList

    def get_shapefile_familynames(self, shpfilename):
        s = os.path.splitext(shpfilename)
        shp = s[0]+".shp"
        dbf = s[0]+".dbf"
        shx = s[0]+".shx"
        return shp, dbf, shx



    def getFileNameInfo(self):
        p = re.compile(r"\w+_(\d+)_(\d+_\d+)_PT.shp")
        for filepath in self.shpFileList:
            file_name = os.path.basename(filepath)
            ru = p.findall(file_name)
            uid = int(ru[0][0])
            print(uid, ru[0][1])
            if  self.user_dic.get(uid) == None :
                self.user_dic[uid] = 1
            else :
                self.user_dic[uid] = self.user_dic[uid] + 1

            print("%d, %d" % (uid , self.user_dic[uid] ))


    def IsDeliverer(self):
        # ** --> recursive dir scan
        #self.getFileNameInfo()

        cc = nvconfig.instance()
        cc._SELECTED_GPS_DIR_PATH


        
        for filepath in self.shpFileList:
            file_name = os.path.basename(filepath)
            gpslist = gpd.read_file(filepath, encoding='cp949' )
            stay_x, stay_y = 0,0
            stay_t = 0
            stay_count = 0
            stay_state = 0
            #동일한 사용자는 gps파일을 연결하여 분석한다.

            for index, row in gpslist.iterrows():
            # 5분이상 1시간 미만동안 이동거리 50m이내인 곳이 5군데 이상있다면 택배로 간주한다.
                x,y = self.transformer.transform(row.geometry.x, row.geometry.y)
                t = datetime.strptime(row.DATETIME, "%Y/%m/%d %H:%M:%S").timestamp()

                if index <= 0 :
                    # last value
                    stay_x, stay_y = x, y
                    stay_t = t
                    continue

                stay_diff_dist = math.sqrt( (x - stay_x) ** 2 + (y - stay_y) ** 2 )
                stay_diff_time = t - stay_t;

                #print("%d %d(%d) %.7f %.7f  %.2f" % (index, t, diff_time, row.geometry.x, row.geometry.y, dist))

                if stay_state == 0 :
                    if stay_diff_dist < 50 :
                        if stay_diff_time > 300 and stay_diff_time < 1800:  # delivered
                            stay_state = 1
                            #print("%d) %d %.7f,%.7f" % (stay_count, index, row.geometry.x, row.geometry.y))
                            #print("%f, %f , %f, %f, %f , %f " % (stay_diff_dist, stay_diff_time, stay_x, stay_y, x, y ))
                            stay_x = x
                            stay_y = y
                            stay_t = t
                            stay_count = stay_count + 1
                        else: # stay_diff_time
                            pass
                    else: # stay_diff_dist >= 50
                        #stay 기준값 초기화
                        stay_x = x
                        stay_y = y
                        stay_t = t
                        pass


                else: # stay_state == 1 :
                    if stay_diff_dist > 50:
                        stay_state = 0
                        stay_x = x
                        stay_y = y
                        stay_t = t
                    else:
                        pass




            if stay_count >= 3 :

                print ("***** stay %d filename : %s"%(stay_count, file_name))


                #file copy

                shp_fnames = self.get_shapefile_familynames(file_name)
                for i, name  in enumerate(shp_fnames):
                    src_filepath = os.path.join(cc._GPSLOG_FILE_PATH, name)
                    target_filepath = os.path.join(cc._SELECTED_GPS_DIR_PATH, name)

                    shutil.copy(src_filepath,target_filepath )
                    if i == 0 :
                        print(src_filepath ,target_filepath)


            # shape file open






