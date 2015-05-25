
from decocare import lib
from decocare import commands
import logging
import time
log = logging.getLogger( ).getChild(__name__)

"""
0x8d == 141 == ReadPumpModel

0000000: 0000 0028 5101 3636 3534 3535 0000 0000  ...(Q.665455....
0000010: 0000 0000 0000 1221 0500 0000 0000 0000  .......!........
0000020: 0700 0000 30a7 6654 558d 001d 0000 0000  ....0.fTU.......
0000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................
"""

"""
0:22.933.038 IN 64

0000000: 4142 433c 5101 3636 3534 3535 0000 0000  ABC<Q.665455....
0000010: 0000 0000 0000 1221 0500 0000 0000 0000  .......!........
0000020: 4000 0000 a503 3532 3200 0000 0000 0000  @.....522.......
0000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................
0:23.203.076 IN 64

0000000: 4142 4325 0000 0000 0000 0000 0000 0000  ABC%............
0000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
0000020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
0000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................

"""
class Framer (object):
  packet_length = -1
  def __init__ (self):
    self._done = False
    self.frames = [ ]
    self.data = bytearray( )

  def frame (self, data):
    head = data[0:3]
    size = data[3]
    load = data[4:4+size]
    payload = bytearray( )
    print "HEAD", head
    if str(head) == 'ABC':
      print "LOAD", load[0]
      last = dict(head=head, size=size, load=load)
      if len(self.frames) < 1:
        query = load[0]
        num  = load[1]
        serial = str(load[2:8])
        meta = data[22:26]
        packet_length = data[32]
        self.packet_length = packet_length
        offset = meta[2]
        payload = data[32+offset:]
        if size < 20 or load[0] < 0x20:
          log.error("UNEXPECTED load")
          return
      else:
        payload = load
      self.data.extend(payload)
      self.frames.append(last)
    if len(self.data) == self.packet_length:
      self._done = True
    if len(self.data) > self.packet_length:
      print "WARNING"
      log.error("self.data bigger than packet_length")
  def done (self):
    return self._done

class Remote (object):
  def __init__ (self, link, serial=None):
    self.link = link
    self.serial = serial

  def execute (self, msg, **kwds):
    msg.serial = self.serial
    message = fmt_command(msg, serial=self.serial, **kwds)
    self.link.write(message)
    framer = Framer( )
    while not framer.done( ):
      data = self.link.read( )
      framer.frame(data)
    print "HYPOTHETICAL PUMP RESULT", framer, len(framer.frames), len(framer.data)
    print lib.hexdump(framer.data)
    msg.respond(framer.data)
    return msg

  def query (self, Msg, **kwds):
    msg = Msg(serial=self.serial, **kwds)
    return self.execute(msg, **kwds)

def fmt_command (msg, serial=None, **kwds):
  prefix = bytearray([ 0x00, 0x00, 0x00 ])
  op = bytearray([ 'Q', 0x01 ]) + bytearray(serial) + \
          bytearray([ 0x00, 0x00, 0x00, 0x00 ]) + \
          bytearray([ 0x00, 0x00, 0x00, 0x00 ]) + \
          bytearray([ 0x00, 0x00 ]) + \
          bytearray([ 0x12, 0x21 ]) + \
          bytearray([ 0x05, 0x00 ]) + \
          bytearray([ 0x00, 0x00 ]) + \
          bytearray([ 0x00, 0x00, 0x00, 0x00 ]) + \
          bytearray([ 0x07, 0x00, 0x00, 0x00 ]) + \
          bytearray([ 0x30, 0xa7 ]) + \
          bytearray(str(serial).decode('hex')) + \
          bytearray([ msg.code, 0x00 ])
  crc = lib.CRC8.compute(op[33:])
  length = bytearray([len(op) + 1])
  return prefix + length + op + bytearray([crc])


if __name__ == '__main__':
  import sys, os
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  from link import Link
  from modem import Modem
  serial = os.environ.get('SERIAL')
  msg = fmt_command(commands.ReadPumpModel(serial=serial), serial=serial)
  print lib.hexdump(msg)

  # sys.exit(0)
  link = Link.Make( )
  # print link.device
  with link:
    modem = Modem(link)
    print modem
    modem.init_modem( )

    with modem.remote( ) as control:

      # now in remote command mode.
      remote = Remote(link, serial)
      model = remote.query(commands.ReadPumpModel)
      print model
      print "MODEL", model.getData( )

      # end remote command mode
