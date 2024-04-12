import logging
from logging.handlers import RotatingFileHandler
import inspect
import os


OUTPUT_LOGFILE_PATH = '.'
OUTPUT_LOGFILE_NAME = 'log'
OUTPUT_LOGFILE_MAX_BYTE = 1024 * 1024
OUTPUT_LOGFILE_BACKUP_COUNT = 2


class Logger():
    """log出力に関するクラス

    クラス作成時に出力したいログレベルが指定されていればそれを
    指定されなければ環境変数から取得したログレベルを出力する

    outputFileがTrueの場合はストリームだけでなくファイルにもログを出力する
    """

    def __init__(self, streamLevel=None, outputFile=False):
        self.__streamLogger = logging.getLogger()
        for handler in self.__streamLogger.handlers:
            self.__streamLogger.removeHandler(handler)
        self.formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s",%(message)s"}')

        # log出力をストリームに送信する設定
        self.__streamHandler = logging.StreamHandler()
        self.__streamHandler.setFormatter(self.formatter)
        self.__streamLogger.addHandler(self.__streamHandler)

        # log出力をファイルに送信する設定
        if outputFile is True:
            self.__rotatingFileHandler = RotatingFileHandler(
                filename=F'{OUTPUT_LOGFILE_PATH}/{OUTPUT_LOGFILE_NAME}.log',
                maxBytes=OUTPUT_LOGFILE_MAX_BYTE,
                backupCount=OUTPUT_LOGFILE_BACKUP_COUNT,
                encoding='utf-8'
            )
            self.__rotatingFileHandler.setFormatter(self.formatter)
            self.__streamLogger.addHandler(self.__rotatingFileHandler)

        if streamLevel is not None:
            self.__streamLogger.setLevel(streamLevel)
        else:
            self._setLogLevelFromEnv()

    def _setLogLevelFromEnv(self):
        logLevel = os.getenv('LOGLEVEL')
        if logLevel == 'DEBUG':
            self.__streamLogger.setLevel(logging.DEBUG)
        elif logLevel == 'INFO':
            self.__streamLogger.setLevel(logging.INFO)
        elif logLevel == 'WARNING':
            self.__streamLogger.setLevel(logging.WARNING)
        elif logLevel == 'ERROR':
            self.__streamLogger.setLevel(logging.ERROR)
        else:
            # 環境変数から見つからない場合のデフォルトはINFOで
            self.__streamLogger.setLevel(logging.INFO)

    def _getLocation(self):
        frame = inspect.currentframe().f_back.f_back
        filename = os.path.basename(frame.f_code.co_filename)
        return '{}, {}, {}'.format(filename, frame.f_code.co_name, frame.f_lineno)

    def writeLogDebug(self, message):
        self._writeLog(logging.DEBUG, message, str(self._getLocation()))

    def writeLogInfo(self, message):
        self._writeLog(logging.INFO, message, str(self._getLocation()))

    def writeLogWarning(self, message):
        self._writeLog(logging.WARNING, message, str(self._getLocation()))

    def writeLogError(self, message):
        self._writeLog(logging.ERROR, message, str(self._getLocation()))

    def _writeLog(self, logLevel, message, location=None):
        if location is None:
            location = str(self._getLocation())

        message ='"location":"' + location + '",' + '"message":"' + str(message)

        if logLevel == logging.DEBUG:
            self.__streamLogger.debug(message)
        elif logLevel == logging.INFO:
            self.__streamLogger.info(message)
        elif logLevel == logging.WARNING:
            self.__streamLogger.warning(message)
        elif logLevel == logging.ERROR:
            self.__streamLogger.error(message)
