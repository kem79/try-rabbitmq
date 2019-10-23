import threading
import sys
import logging
import uuid
import os
from inspect import getframeinfo, stack, getargspec
from functools import wraps

logger_info = threading.local()

def get_trace_id(create_if_none=False):
  """get trace id from thead local

  :param create_if_none: generate one by `uuid.uuid1()` if no trace id
                         exists
  """
  result = None
  if hasattr(logger_info, 'trace_id'):
    result = logger_info.trace_id
  else:
    result = None if not create_if_none else str(uuid.uuid1())
    if result is not None:
      logger_info.trace_id = result

  return result

def set_trace_id(trace_id=None):
  """set trace id in thread local

  :param trace_id: trace id, will generate one by
                  `uuid.uuid1()` if not passed
  """
  if trace_id is None:
    trace_id = str(uuid.uuid1())

  logger_info.trace_id = str(trace_id)
  return trace_id

def clean_trace_id():
  """clean the trace id from the thread local"""
  logger_info.trace_id = None

def with_trace_id(func):
  def __handle_kwargs(kwargs):
    # delete trace_id param in case original `func` takes no arguments
    trace_id = kwargs.pop('trace_id', None)
    if trace_id is not None:
      set_trace_id(trace_id)

  arg_spec = getargspec(func)

  if 'self' in arg_spec.args:
    """set up trace id"""
    @wraps(func)
    def __decorated_func_with_self(self, *args, **kwargs):
      __handle_kwargs(kwargs)
      return func(self, *args, **kwargs)

    return __decorated_func_with_self

  else:
    """set up trace id"""
    @wraps(func)
    def __decorated_func(*args, **kwargs):
      __handle_kwargs(kwargs)
      return func(*args, **kwargs)

    return __decorated_func

class TraceableLogger:
  """a logger to print traceable log in distributed system

  output logs to the stdout with following format
  YYYY-MM-DD HH:MM:SS,sss [levelname] message filename line_number trace_id
  e.g:
  2018-10-10 01:42:09,842 [INFO] creat thread __init__.py 39

  :param name: logger name
  :param level: standard log level
  """
  def __init__(
    self,
    name,
    instance_guid="default",
    level=os.getenv('APP_LOG_LEVEL', logging.INFO)
  ):
    self.name = name
    self.level = level
    self.instance_guid = instance_guid
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    log_format = '%(asctime)-15s [%(levelname)s] %(message)s %(caller_filename)s %(caller_lineno)d %(traceid)s %(instance_guid)s %(pid)d'
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    self.logger = logger

  def _log(self, message, log_method_name='info', trace_id=None):
    """output message to stdout with given log level

    output logs to the stdout with following format
    YYYY-MM-DD HH:MM:SS,sss [levelname] message filename line_number trace_id
    e.g:
    2018-10-10 01:42:09,842 [INFO] creat thread __init__.py 39

    :param log_method_name: one of `debug`, `info`, `error`, `warning`,
                            `critical`, `exception`
    :param trace_id: the uid will be appended to the message, will generate one by
                     `uuid.uuid1()` if not passed
    """
    trace_id = trace_id if trace_id is not None else get_trace_id(True)
    caller = getframeinfo(stack()[2][0])
    extra_params = {
      'traceid': trace_id,
      'caller_filename': caller.filename,
      'caller_lineno': caller.lineno,
      'instance_guid': os.getenv("CF_INSTANCE_GUID", "default"),
      'pid': os.getpid()
    }
    log_method = getattr(self.logger, log_method_name)
    log_method(message, extra=extra_params)

  def debug(self, message, trace_id=None):
    """output message to stdout with given debug level"""
    self._log(message, 'debug', trace_id)

  def info(self, message, trace_id=None):
    """output message to stdout with given info level"""
    self._log(message, 'info', trace_id)

  def error(self, message, trace_id=None):
    """output message to stdout with given error level"""
    self._log(message, 'error', trace_id)

  def warning(self, message, trace_id=None):
    """output message to stdout with given warning level"""
    self._log(message, 'warning', trace_id)

  def critical(self, message, trace_id=None):
    """output message to stdout with given critical level"""
    self._log(message, 'critical', trace_id)

  def exception(self, message, trace_id=None):
    """output message to stdout with given error level"""
    self._log(message, 'exception', trace_id)