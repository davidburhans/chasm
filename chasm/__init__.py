'''
Chasm is a mixin that automatically creates a client
'''
import asyncio
import asyncio.streams

from collections import deque, namedtuple
from functools import wraps, partial, lru_cache
from inspect import signature
from types import FunctionType, MethodType
from uuid import uuid4

try:
  import ujson as json
except ImportError:
  import json

def fn_to_name(fn):
  assert fn.__self__.__class__.__name__, 'must be called on an instance of ChasmMixin'
  assert fn.__name__, 'method must be named'
  return '.'.join([fn.__self__.__class__.__name__, fn.__name__])

loop = asyncio.get_event_loop()
EOR = '\n'
PORT = 55555

ChasmMessage = namedtuple('ChasmMessage', 'name args kwargs request_id')
ChasmResponse = namedtuple('ChasmMessage', 'request_id name response')


def encode_message(msg):
  if not isinstance(msg, ChasmMessage):
    ChasmMessage(msg)
  return json.dumps(msg, sort_keys=True)
  

def encode_response(orig_msg, response=None):
  if not isinstance(orig_msg, ChasmMessage):
    orig_msg = ChasmMessage(orig_msg)
  response = ChasmResponse(orig_msg.request_id, orig_msg.name, response)
  return json.dumps(response, sort_keys=True)


def decode_message(msg_str):
  return ChasmMessage(json.loads(msg_str))


def decode_response(response_str):
  return ChasmResponse(json.loads(response_str))


class ChasmMixin:
  @classmethod
  def Client(cls, *args, **kwargs):
    def __init__(self, *args, **kwargs):
      super(self.__class__, self).__init__(*args, **kwargs)
      for name, fn in self.__class__.__dict__.items():
        if not name.startswith('_') and type(fn) == FunctionType:
          setattr(self, name, self._wrap(getattr(self, name)))

    def _wrap(self, fn):
      @wraps(fn)
      def wrapper(*args, **kwargs):
        wrapper.__signature__.bind(*args, **kwargs)
        assert callable(fn), 'must wrap callable'
        name = fn_to_name(fn)
        request_id = ChasmSpooler.get().queue_request(name, *args, **kwargs)
        # wait for callback
      wrapper.__signature__ = signature(fn)
      return wrapper

    proxied_funcs = dict()
    for name, fn in getattr(cls, '__dict__', {}).items():
      if not name.startswith('_') and type(fn) == FunctionType:
        proxied_funcs[name] = fn
    proxied_funcs['_wrap'] = _wrap
    proxied_funcs['__init__'] = __init__
    client = type(cls.__name__, (), proxied_funcs)
    return client(*args, **kwargs)
