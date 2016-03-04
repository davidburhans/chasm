import asyncio

from chasm import decode_message, decode_response, EOR, PORT, loop


def get_host_class(name, scope=None):
  try:
    names = name.split('.')
    n = names[0]
    remaining = '.'.join(names[1:])
  except ValueError:
    n = name,
    remaining = ''
  obj = None
  try:
    next_scope = scope.get(n)
  except AttributeError:
    next_scope = getattr(scope, n)
  if '.' in remaining:
    return get_host_class(remaining, scope=next_scope)
  return next_scope, remaining


class ChasmServer:
  def __init__(self, *hosts_to_serve):
    self.sever = None
    self.clients = dict()
    self._hosts = dict()
    for host in hosts_to_serve:
      self._hosts[host.__name__] = host()

  def _accept(self, client_reader, client_writer):
    task = asyncio.Task(self._handle_client(client_reader, client_writer))
    self.clients[task] = (client_reader, client_writer)
    task.add_done_callback(self._disconnect)

  def _disconnect(self, task):
    del self.clients[task]

  def _invoke_message(self, request_data):
    name, args, kwargs, request_id = request_data

    cls, fn = get_host_class(name, scope=???)
    if not self._hosts.has_key(cls):
      self._hosts[cls] = cls()

    return getattr(self._hosts[cls], fn)(*args, **kwargs)

  @asyncio.coroutine
  def _handle_client(self, client_reader, client_writer):
    while True:
        data_str = (yield from client_reader.readline()).decode("utf-8")
        if not data_str: # an empty string means the client disconnected
            break
        data = decode_message(data_str)

        response_str = ''
        try:
          response = self._invoke_message(data)
          response_str = encode_response(data, response=response)
        except Exception as e:
          response_str = encode_response(data, response=dict(exception=e.message))
          
        # if host[fn_name] needs response
        client_writer.write((response_str + EOR).encode('utf-8'))
        # This enables us to have flow control in our connection.
        yield from client_writer.drain()

  def listen(self, addr='127.0.0.1', port=PORT, loop=loop, block=False):
    self.server = loop.run_until_complete(
      asyncio.streams.start_server(
        self._accept,
        addr,
        port,
        loop=loop
        )
      )
    if block:
      loop.run_until_complete(self.server.wait_closed())

  def close(self, loop):
    if self.server is not None:
      self.server.close()
      loop.run_until_complete(self.server.wait_closed())
      self.server = None