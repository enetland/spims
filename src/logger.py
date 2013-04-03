import logging
from time import strftime
import os

class Singleton:
  """
  A non-thread-safe helper class to ease implementing singletons.
  This should be used as a decorator -- not a metaclass -- to the
  class that should be a singleton.

  The decorated class can define one `__init__` function that
  takes only the `self` argument. Other than that, there are
  no restrictions that apply to the decorated class.

  To get the singleton instance, use the `Instance` method. Trying
  to use `__call__` will result in a `TypeError` being raised.

  Limitations: The decorated class cannot be inherited from.

  """

  def __init__(self, decorated):
    self._decorated = decorated

  def Instance(self):
    """
    Returns the singleton instance. Upon its first call, it creates a
    new instance of the decorated class and calls its `__init__` method.
    On all subsequent calls, the already created instance is returned.
    """
    try:
      return self._instance
    except AttributeError:
      self._instance = self._decorated()
      return self._instance

  def __call__(self):
    raise TypeError('Singletons must be accessed through `Instance()`.')

  def __instancecheck__(self, inst):
    return isinstance(inst, self._decorated)


@Singleton
class Logger:
  def __init__(self):

    if not os.path.exists("log"):
      os.makedirs("log")

    l = logging.getLogger("spims")
    l.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')

    # Stream handler reports log messages to stdout.
    stream_handler = logging.StreamHandler()
    # NOTE: For assignment handin the log level should be set to ERROR.
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(fmt)
    l.addHandler(stream_handler)

    # Stream handler reports log messages to file in log directory.
    # Each execution of spims gets its own log file.
    file_name = "log/" + strftime("%d_%b_%Y_%H:%M:%S") + ".log"
    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    l.addHandler(file_handler)

    self.logger = l

  def debug(self,m):
    self.logger.debug(m)
  def info(self,m):
    self.logger.info(m)
  def warning(self,m):
    self.logger.warning(m)
  # As specified in the requirements of this project, we should exit with
  # program with exit code 1 and report the error.
  def error(self,m):
    self.logger.error(m)
    exit(1)
  def critical(self,m):
    self.logger.critical(m)
    exit(1)
