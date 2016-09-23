import logging

from Orchestrator import Orchestrator

# Let's add a notice log level because boto is to verbose at info level
NOTICE = logging.INFO + 1


# http://stackoverflow.com/a/35804945
def logForLevel(self, message, *args, **kwargs):
    if self.isEnabledFor(levelNum):
        self._log(levelNum, message, args, **kwargs)


def logToRoot(message, *args, **kwargs):
    logging.log(levelNum, message, *args, **kwargs)


levelName = 'NOTICE'
levelNum = NOTICE
methodName = levelName.lower()
logging.addLevelName(levelNum, levelName)
setattr(logging, levelName, levelNum)
setattr(logging.getLoggerClass(), methodName, logForLevel)
setattr(logging, methodName, logToRoot)
