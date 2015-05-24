
from decocare import lib
import logging
log = logging.getLogger( ).getChild(__name__)

class Command (object):
  pass

class Response (object):
  pass

class Transmission (object):
  Response = Response
  Command = Command

  def __init__ (self, Response=None, Command=None):
    if Response:
      self.Response = Response
    if Command:
      self.Command = Command
  def send (self):
    msg = self.command
  def __call__ (self, link):
    self.command = self.Command( )
    self.response = self.Response( )

class StopResponses (Response):
  MODES = [ 0x05, 0x04 ]
  def __init__ (self):
    self._done = False
    self.frames = [ ]
    pass
  def frame (self, data):
    head = data[0:3]
    size = data[3]
    load = data[4:4+size]
    print "HEAD", head
    if str(head) == 'ABC':
      print "LOAD", load[0]
      last = dict(head=head, size=size, load=load)
      self.frames.append(last)
      if size == 1:
        if load[0] in self.MODES:
          self._done = True

  def done (self):
    return self._done

class TransferMode (Transmission):
  Response = StopResponses
  def __call__ (self, link):
    self.response = self.Response( )
    print "writing"
    # link.write(bytearray([0x00, 0x00, 0x00, 0x01, 'X']))
    # link.write(bytearray([0x00, 0x00, 0x00, 0x01, 0x06]))
    while not self.response.done( ):
      print "reading"
      data = link.read( )
      self.response.frame(data)
    return self

class ACK (Command):
  op = 06

class ENQ (Command):
  op = 05

class NAK (Command):
  op = 15

class EOT (Command):
  op = 04
class Stop (Transmission):
  Command = NAK

class TransferModeStop (Transmission):
  Response = StopResponses
  def __call__ (self, link):
    self.response = self.Response( )
    print "writing"
    link.write(bytearray([0x00, 0x00, 0x00, 0x01, 'X']))
    while not self.response.done( ):
      print "reading"
      data = link.read( )
      self.response.frame(data)
    return self

class Modem (object):
  def __init__ (self, link):
    self.link = link

  def execute (self, exchange):
    return exchange(self.link)

if __name__ == '__main__':
  import sys
  from link import Link
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  link = Link.Make( )
  # print link.device
  with link:
    modem = Modem(link)
    print modem
    result = modem.execute(TransferModeStop( ))
    link.write(bytearray([ 0x00, 0x00, 0x00, 0x01, 0x15 ]))
    # result = modem.execute(TransferModeStop( ))
    # link.write(bytearray([ 0x00, 0x00, 0x00, 0x01, 0x06 ]))
    result = modem.execute(TransferMode( ))
    print "XYXYXYX"
    print result.response.frames[-1], result.response.frames[-1].get('load')
    last_ack = result.response.frames[-1].get('load')[0]
    if last_ack == 0x04:
      link.write(bytearray([ 0x00, 0x00, 0x00, 0x01, 0x05 ]))
      link.read( )
      # result = modem.execute(TransferMode( ))
    else:
      link.write(bytearray([ 0x00, 0x00, 0x00, 0x01, 0x15 ]))
      link.read( )
      link.write(bytearray([ 0x00, 0x00, 0x00, 0x01, 0x05 ]))
      link.read( )
    # now in remote command mode.

    link.write(bytearray([ 0x00, 0x00, 0x00, 0x02, "W", "|" ]))
    link.read( )
    link.write(bytearray([ 0x00, 0x00, 0x00, 0x02, "Q", "|" ]))
    link.read( )
    link.write(bytearray([ 0x00, 0x00, 0x00, 0x02, "1", "|" ]))
    link.read( )
    # link.write(bytearray([ 0x00, 0x00, 0x00, 0x02, "0", "|" ]))
    # link.read( )
    # link.write(bytearray([ 0x00, 0x00, 0x00, 0x01, 0x05 ]))
    # link.read( )
    # end remote command mode
    link.write(bytearray([ 0x00, 0x00, 0x00, 0x02, "\r", 0x04 ]))
    link.read( )
    #link.write(bytearray([ 0x00, 0x00, 0x00, 0x01, 0x15 ]))
    #result = modem.execute(TransferMode( ))
    """

    # the following seems to help exit 
    link.write(bytearray([ 0x00, 0x00, 0x00, 0x01, 0x05 ]))
    result = modem.execute(TransferMode( ))
    link.write(bytearray([ 0x00, 0x00, 0x00, 0x01, 0x15 ]))
    link.read( )
    print "will reset in 5 minutes or so"
    """
    print result
