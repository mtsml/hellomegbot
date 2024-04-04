import logging
import inspect
import os


class Logger():
    """log出力に関するクラス

    クラス作成時に出力したいログレベルが指定されていればそれを
    指定されなければ環境変数から取得したログレベルを出力する
    """

    def __init__(self, streamLevel=None):
        self.__streamLogger = logging.getLogger()
        for handler in self.__streamLogger.handlers:
            self.__streamLogger.removeHandler(handler)
        self.formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s",%(message)s"}')
        self.__streamHandler = logging.StreamHandler()
        self.__streamHandler.setFormatter(self.formatter)
        self.__streamLogger.addHandler(self.__streamHandler)

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
