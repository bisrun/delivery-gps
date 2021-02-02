import configparser
import os

class nvconfig :

    _instance = None

    @classmethod
    def _getInstance(cls):
        return cls._instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls._instance = cls(*args, **kargs)
        cls.instance = cls._getInstance
        return cls._instance

    def setInit(self, config_file_path):
        self._config_file_path =os.path.join(os.getcwd(), 'nvconfig.ini')

        if config_file_path != '':
            self._config_file_path = config_file_path

    def load_file(self):
        try:
            config = configparser.ConfigParser()
            config.read(self._config_file_path, 'utf-8')

            network_dir_path = config['NETWORK_SRC']['NETWORK_SRC_DIR_PATH']


            output_dir_path = config['OUTPUT']['OUTPUT_DIR_PATH']
            self._GPSLOG_FILE_PATH = config['NETWORK_SRC']['GPS_DIR_PATH']
            self._SELECTED_GPS_DIR_PATH =  config['NETWORK_SRC']['SELECTED_GPS_DIR_PATH']

            self._LOG_FILE_PATH = os.path.join(output_dir_path, config['OUTPUT']['LOG_FILE_NAME'])



            # 입력파일 검증
            '''
            if os.path.exists(self._LINK_FILE_PATH) == False:
                print(self._LINK_FILE_PATH + ' 파일이 없습니다.')
                return -1
            if os.path.exists(self._NODE_FILE_PATH) == False:
                print(self._NODE_FILE_PATH + ' 파일이 없습니다.')
                return -1
            if os.path.exists(self._HDONG_FILE_PATH) == False:
                print(self._HDONG_FILE_PATH + ' 파일이 없습니다.')
                return -1
            if os.path.exists(self._DUST_FILE_PATH) == False:
                print(self._DUST_FILE_PATH + ' 파일이 없습니다.')
                return -1
            '''


            if os.path.isdir(output_dir_path) == False:
                os.makedirs(os.path.join(output_dir_path))



            return 0
        except KeyboardInterrupt:
            print('\n\rquit')

def run():
    try:

        cc = nvconfig('')
        #cc = cleanrp_config('')
        cc.load_file()

        

        print(cc._LINK_FILE_PATH)
        print(cc._NODE_FILE_PATH)

        print(cc._HDONG_FILE_PATH)

        print(cc._WEATHER_DB_IP)
        print(cc._WEATHER_DB_USER_ID)
        print(cc._WEATHER_DB_PASSWD)

        print(cc._CMESH_PT_FILE_PATH)
        print(cc._CMESH_RECT_FILE_PATH)
        print(cc._DUST_HDONG_PT_FILE_PATH)
        print(cc._DUST_CMESH_PT_FILE_PATH)
        print(cc._DUST_LINK_PT_FILE_PATH)
        print(cc._DUST_LINK_TXT_FILE_PATH)

        print('complete !!')

    except KeyboardInterrupt:
        print('\n\rquit')


if __name__ == '__main__':
    run()