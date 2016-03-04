import asyncio
from chasm import encode_message, decode_message, decode_response, EOR
class ChasmClient:
  def __init__(self, addr='127.0.0.1', port=PORT, loop=loop):
    self.reader, self.writer = yield from asyncio.stream.open_connection(
      addr, port, loop)

  def send(self, msg):
    self.writer.write((encode_message(msg) + EOR).encode('utf-8'))

  def query(self, msg):
    self.writer.write((encode_message(msg) + EOR).encode('utf-8'))
    return self.query_response()

  def query_response(self):
    result_str = (yield from self.reader.readline()).decode("utf-8").rstrip()
    return decode_response(result_str)