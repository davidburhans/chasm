from collections import deque
import json

from chasm import build_host_obj

class ChasmSpooler:
  queue = deque()
  response = dict()
  _instance = None
  _server = {}

  @classmethod
  def get(cls):
    if not getattr(cls, '_instance'):
      cls._instance = cls()      
    return cls._instance

  def __init__(self, addr='127.0.0.1', port=PORT, loop=loop):
    self.client = ChasmClient(addr=addr, port=port, loop=loop)

  def queue_request(self, name, *args, **kwargs):
    request_id = str(uuid4())
    to_queue = json.dumps((name, args, kwargs, request_id))
    self.queue.appendleft(to_queue)
    print('queued', to_queue)
    self.unspool()
    return request_id

  def unspool(self):
    while len(self.queue) > 0:
      name, args, kwargs, request_id = json.loads(self.queue.pop())
      obj_name = name[0:name.rindex('.')]
      fn_name = name.replace(obj_name + '.', '')
      if not self._server.get(obj_name):
        self._server[obj_name] = build_host_obj(obj_name)
      self.response[name] = getattr(self._server[obj_name], fn_name)(*args, **kwargs)

  def get_response(self, name):
    return self.response.pop(name)