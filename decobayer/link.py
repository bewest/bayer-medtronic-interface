
"""
Borrowed heavily from glucodump.
https://bitbucket.org/iko/glucodump/src/ce8da3e63217098a844a9cdea99f90c5ee5d20c6/glucodump/usbcomm.py?at=default
"""

import usb
from decocare import lib, link
import logging
log = logging.getLogger( ).getChild(__name__)

from collections import namedtuple

Description = namedtuple('Description', ['vendor', 'product'])
BayerContour = Description(0x1a79, 0x6002)
BayerContourNextlink = Description(0x1a79, 0x6200)

class Link (link.Link):
    blocksize = 64
    candidates = dict(contour=BayerContour, nextlink=BayerContourNextlink)
    
    def __init__(self, device):
      self.device = device

    @classmethod
    def scan (klass):
        for name, description in klass.candidates.items( ):
            sniff = klass.find(idProduct=description.product, idVendor=description.vendor)
            if sniff:
              return sniff
        return None

    def __enter__ (self):
        self.open( )
        return self

    def __exit__ (self, type, value, tb):
        self.close( )

    @classmethod
    def find (klass, **kw):
        return usb.core.find(**kw)
        dev = usb.core.find(**kw)
        self.dev = dev
        print dev
        self.product = kw['idProduct']
        self.vendor = kw['idVendor']

    @classmethod
    def Make (klass, auto_acquire=False):
      candidate = klass.scan( )
      link = Link(candidate)
      if candidate:
        if auto_acquire:
          link.acquire( )
        return link

    def open (self):
        self.acquire( )
        return self

    def acquire (self):
        try:
            self.device.set_configuration()
        except usb.core.USBError:
            pass
        config = self.device.get_active_configuration()
        interface = usb.util.find_descriptor(config,
                                             bInterfaceClass=usb.CLASS_HID)
        if self.device.is_kernel_driver_active(interface.index):
            self.device.detach_kernel_driver(interface.index)

        interface.set_altsetting()
        usb.util.claim_interface(self.device, interface)
        self.interface = interface

        self.epin = usb.util.find_descriptor(interface, bEndpointAddress=0x81)
        self.epout = usb.util.find_descriptor(interface, bEndpointAddress=0x01)

    def close(self):
        usb.util.release_interface(self.device, self.interface)
        usb.util.dispose_resources(self.device)
    def write (self, data):
        log.info('WRITE %s\n%s' % (len(data), lib.hexdump(data)))
        self.epout.write(data)
    def glucodump_write(self, data):
        remain = data
        while remain:
            now = remain[:self.blocksize-4]
            remain = remain[self.blocksize-4:]
            self.epout.write('\0\0\0' + chr(len(now)) + now) # + ('\0' * (self.blocksize - 4 - len(now))))
    def read (self):
        data = bytearray(self.epin.read(self.blocksize))
        log.info('READ %s\n%s' % (len(data), lib.hexdump(data)))
        return data
    def glucodump_read (self):
        result = []
        while True:
            data = self.epin.read(self.blocksize)
            dstr = data.tostring()
            #assert dstr[:3] == 'ABC'
            print '<<<', repr(dstr)
            result.append(dstr[4:data[3]+4])
            if data[3] < 2 or result[-1][-2:].encode('hex') == "0d0a":
                break

        return ''.join(result)

if __name__ == '__main__':
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    link = Link.Make( )
    print link.device
    with link:
      print link

