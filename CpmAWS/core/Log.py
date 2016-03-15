import logging

class Log(logging.getLoggerClass()):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)

        logging.addLevelName(NOTICE, "NOTICE")

    def notice(self, msg, *args, **kwargs):
        if self.isEnabledFor(NOTICE):
            self._log(NOTICE, msg, args, **kwargs)


def logForLevel(self, message, *args, **kwargs):
    if self.isEnabledFor(levelNum):
        self._log(levelNum, message, args, **kwargs)


def logToRoot(message, *args, **kwargs):
    logging.log(levelNum, message, *args, **kwargs)


levelName = 'NOTICE'
levelNum = NOTICE
logging.addLevelName(levelNum, levelName)
setattr(logging, levelName, levelNum)
setattr(logging.getLoggerClass(), methodName, logForLevel)
setattr(logging, methodName, logToRoot)
