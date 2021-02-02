import os
import pandas as pd
import numpy as np

from shapely.geometry import Point
from cleanrp_mesh import cleanrp_mesh
from nvconfig import nvconfig
from nvlogger import Logger
import ogr


class cleanrp_cmesh_link :

    def __init__(self, cc):
        self._config_file_path =os.path.join(os.getcwd(), 'nvconfig.ini')
        self._cc = cc
        logManager = Logger.instance()
        self._logger = logManager.getLogger()


    def load_file(self):
        try:

            # 입력파일 검증
            if os.path.exists(self._cc._HDONG_FILE_PATH) == False:
                print(self._cc._HDONG_FILE_PATH + ' 파일이 없습니다.')
                return -1
            if os.path.exists(self._cc._CMESH_PT_FILE_PATH) == False:
                print(self._cc._CMESH_PT_FILE_PATH + ' 파일이 없습니다.')
                return -1
            if os.path.exists(self._cc._LINK_FILE_PATH) == False:
                print(self._cc._LINK_FILE_PATH + ' 파일이 없습니다.')
                return -1
            if os.path.exists(self._cc._NODE_FILE_PATH) == False:
                print(self._cc._NODE_FILE_PATH + ' 파일이 없습니다.')
                return -1


            # EPSG:4326
            self._logger.info("load bdong shp")
            bdong_shp = gpd.read_file(self._cc._HDONG_FILE_PATH)
            bdong_shp.crs = {'init': 'epsg:4326'}

            self._logger.info("load cmesh shp")
            cmesh_shp = gpd.read_file(self._cc._CMESH_PT_FILE_PATH)
            cmesh_shp.crs = {'init': 'epsg:4326'}

            selected_col = ['H_CODE', 'geometry']
            bdong_shp = bdong_shp[selected_col]

            file_in_link = self._cc._LINK_FILE_PATH
            file_in_node = self._cc._NODE_FILE_PATH
            file_out_link_mesh =self._cc._LINK_CMESH_PT_FILE_PATH
            file_out_link_mesh_txt =self._cc._LINK_CMESH_TXT_FILE_PATH
            hdong_cmesh_fp_shp = self._cc._HDONG_CMESH_PT_FILE_PATH
            if os.path.isfile(file_out_link_mesh):
                os.remove(file_out_link_mesh);

            #Load NODE text
            self._logger.info("load node txxt")
            node = pd.read_csv(file_in_node, sep='|', engine='python',
                               usecols=['NODE_ID', 'X', 'Y'], encoding='cp949')
            pts_geom = [Point(xy) for xy in zip(node.X, node.Y)]
            # Make NODE shape
            geom_df = gpd.GeoDataFrame(node, geometry=pts_geom)
            geom_df.crs = {'init': 'epsg:4326'}
            geom_df['CMID'] = (geom_df['X'] * 100).astype(int) * 100000 + geom_df['Y'] * 100
            geom_df['CMID'] = geom_df.CMID.astype(int)

            #make cmesh-hdong shape
            self._logger.info("make cmesh-hdong shp")
            cmesh_hdong = gpd.sjoin(cmesh_shp, bdong_shp, how="inner", op="within")
            cmesh_hdong.to_file(driver='ESRI Shapefile', filename=hdong_cmesh_fp_shp)

            #Load Link txt
            self._logger.info("load link txt")
            link = pd.read_csv(file_in_link, sep='|', engine='python',
                               usecols=['LINK_ID', 'FROM_NODE_ID', 'TO_NODE_ID', 'ROUTE_ROAD_CATE'], encoding='cp949')
            # Join Link - cmid
            self._logger.info("join link-cmid txt")
            link_cmid = pd.merge(link, geom_df, how='inner', left_on='FROM_NODE_ID', right_on='NODE_ID')

            self._logger.info("make link-cmid txt")
            link_cmid = link_cmid.drop(['FROM_NODE_ID','TO_NODE_ID','NODE_ID','X','Y'], axis=1)
            link_cmid.to_csv( file_out_link_mesh_txt, mode="w", columns=['LINK_ID', 'CMID','geometry'])

            """
            #Make Link shape but shapetype is a point of from_node
            self._logger.info("make link-cmid shp")
            geom_link_cmid = gpd.GeoDataFrame(link_cmid, geometry=link_cmid.geometry)
            self._logger.info("make link-cmid shp-1")
            geom_link_cmid = geom_link_cmid.drop(['NODE_ID'], axis=1)
            self._logger.info("make link-cmid shp-2")
            #geom_link_cmid.to_file(driver='ESRI Shapefile', filename=file_out_link_mesh)
            self.write_link_cmid(geom_link_cmid)
            """

            self._logger.info("complete to make link-cmid/hdong-cmid shp")
        except KeyboardInterrupt:
            print('\n\rquit')


class cleanrp_rtwi :

    def __init__(self, cc):
        self._config_file_path =os.path.join(os.getcwd(), 'nvconfig.ini')
        self._cc = cc
        logManager = Logger.instance()
        self._logger = logManager.getLogger()


    def load_file(self):
        try:
            # 입력파일 검증
            if os.path.exists(self._cc._HDONG_FILE_PATH) == False:
                print(self._cc._HDONG_FILE_PATH + ' 파일이 없습니다.')
                return -1
            if os.path.exists(self._cc._HDONG_CMESH_PT_FILE_PATH) == False:
                print(self._cc._HDONG_CMESH_PT_FILE_PATH + ' 파일이 없습니다.')
                return -1
            if os.path.exists(self._cc._LINK_CMESH_TXT_FILE_PATH) == False:
                print(self._cc._LINK_CMESH_TXT_FILE_PATH + ' 파일이 없습니다.')
                return -1



            self._logger.info("load bdong shp")
            bdong_shp = gpd.read_file(self._cc._HDONG_FILE_PATH)
            bdong_shp.crs = {'init': 'epsg:4326'}

            self._logger.info("load dust info")
            dust = pd.read_csv(self._cc._DUST_FILE_PATH, sep=',', engine='python', usecols=['REG_ID', 'UV', 'PM10', 'PM2_5', 'CAI', 'CAI_VAL'],
                               dtype={'REG_ID': str})
            dust = dust.rename(columns={'REG_ID': 'H_CODE'})

            self._logger.info("join dust-hdong for debugging ^^;;")
            dust_hdong = pd.merge(bdong_shp, dust, how='inner', left_on='H_CODE', right_on='H_CODE')
            geom_dust_hdong = gpd.GeoDataFrame(dust_hdong, geometry=dust_hdong.geometry)
            geom_dust_hdong.to_file(driver='ESRI Shapefile', filename=self._cc._DUST_HDONG_PT_FILE_PATH)

            self._logger.info("load hdong_cmesh info")
            cmesh_hdong = gpd.read_file(self._cc._HDONG_CMESH_PT_FILE_PATH)
            cmesh_hdong.crs = {'init': 'epsg:4326'}

            self._logger.info("load link_cmesh info")
            link_cmid = pd.read_csv(self._cc._LINK_CMESH_TXT_FILE_PATH, engine='python')

            self._logger.info("join dust-cmid info")
            dust_cmid = pd.merge(dust, cmesh_hdong, how='inner', left_on='H_CODE', right_on='H_CODE')
            geom_dust_cmid = gpd.GeoDataFrame(dust_cmid, geometry=dust_cmid.geometry)
            geom_dust_cmid.to_file(driver='ESRI Shapefile', filename=self._cc._DUST_CMESH_PT_FILE_PATH)

            self._logger.info("join dust-link info")
            link_dust = pd.merge(link_cmid, dust_cmid, how='inner', on='CMID')
            #link_dust = link_dust.drop(['geometry_x','index_right','geometry_y'])
            self._logger.info("make dust-link txt")
            link_dust.to_csv( self._cc._DUST_LINK_TXT_FILE_PATH, mode="w", columns=['LINK_ID', 'UV','PM10', 'PM2_5','CAI', 'CAI_VAL','CMID'])


            self._logger.info("complete to make dust-link/hdong-cmid shp")
        except KeyboardInterrupt:
            print('\n\rquit')

    def linkshp_exp(self):
        try:
            # 입력파일 검증
            if os.path.exists(self._cc._LINK_SHP_FILE_PATH) == False:
                print(self._cc._LINK_SHP_FILE_PATH + ' 파일이 없습니다.')
                return -1

            self._logger.info("load link shp")
            link_shp = gpd.read_file(self._cc._LINK_SHP_FILE_PATH)
            link_shp.crs = {'init': 'epsg:4326'}

            self._logger.info("load link_dust info")
            dust_link = pd.read_csv(self._cc._DUST_LINK_TXT_FILE_PATH, sep=',', engine='python',
                               usecols=['LINK_ID', 'CAI_VAL','CMID']) #'UV', 'PM10', 'PM2_5', 'CAI',

            self._logger.info("load all")

            link_shp['LINK_ID'] = link_shp['LINK_ID'].astype(np.int64)
            link_dust_line = pd.merge(link_shp, dust_link, how='inner', on='LINK_ID')

            self._logger.info("make link shape by ogr")
            drv = ogr.GetDriverByName('ESRI Shapefile')
            ds = drv.CreateDataSource(self._cc._DUST_LINK_LINE_FILE_PATH)
            lyr = ds.CreateLayer('myshp', geom_type=ogr.wkbLineString)

            fieldDef = ogr.FieldDefn('LINK_ID', ogr.OFTInteger64)
            lyr.CreateField(fieldDef)
            fieldDef = ogr.FieldDefn('CAI_VAL', ogr.OFTInteger)
            lyr.CreateField(fieldDef)
            fieldDef = ogr.FieldDefn('CMID', ogr.OFTString)
            lyr.CreateField(fieldDef)

            for index, item in link_dust_line.iterrows():
                feat = ogr.Feature(lyr.GetLayerDefn())
                feat.SetField('LINK_ID', item['LINK_ID'])
                feat.SetField('CAI_VAL', item['CAI_VAL'])
                feat.SetField('CMID', item['CMID'])
                #pt = ogr.CreateGeometryFromWkt(item['geometry'])
                line = ogr.CreateGeometryFromWkb(item['geometry'].to_wkb())
                feat.SetGeometry(line)
                lyr.CreateFeature(feat)

                feat = None

            self._logger.info("complete to make link shape by ogr")
        except KeyboardInterrupt:
            print('\n\rquit')


def run(step):
    try :
        pd.set_option('display.max_columns', 12)
        cc = nvconfig('')
        ret = cc.load_file()
        if ret < 0 :
            return -1

        logManager = Logger.instance()
        logManager.setLogger(cc._LOG_FILE_PATH)
        logger = logManager.getLogger()
        logger.debug("debug test")

        my_step = 1
        if  step <= my_step  :
            cm = cleanrp_mesh(0.01)
            cm.create_point_shp(cc._CMESH_PT_FILE_PATH)

        my_step = 2
        if  step <= my_step  :
            cmesh_link = cleanrp_cmesh_link(cc)
            cmesh_link.load_file()

        my_step = 3
        if  step <= my_step  :
            dust_link = cleanrp_rtwi(cc)
            dust_link.load_file()
            dust_link.linkshp_exp()


    except KeyboardInterrupt:
        print('\n\rquit')


if __name__ == '__main__':
    run(3)