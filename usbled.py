#!/usr/bin/python

import usb
import sys

CMD_ECHO  = 0
CMD_GET   = 1 
CMD_SET   = 2 
CMD_CLEAR = 3 
CMD_RESET = 4


class usb_dev:
    def __init__(self, vendor_id, device_id, interface_id):
        self.vendor_id = vendor_id
        self.device_id = device_id
        self.interface_id = interface_id

    def get_device(self):
        buses = usb.busses()
        for bus in buses:
            for dev in bus.devices:
                if dev.idVendor == self.vendor_id and \
                    dev.idProduct == self.device_id:
                    return dev
        return None

class usb_led:
    VENDOR_ID = 0x16c0
    DEVICE_ID = 0x0501
    INTERFACE_ID = 0

    device_descriptor = usb_dev(VENDOR_ID, DEVICE_ID, INTERFACE_ID);

    def __init__(self):
        self.device = self.device_descriptor.get_device()
        self.handle = None

    def open(self):
        if not self.device:
            self.device = self.device_descriptor.get_device()
        if not self.device:
            print >> sys.stderr, "Device Not Found."
            return

        devname = ""

        try:
            self.handle = self.device.open()
            self.handle.claimInterface(self.device_descriptor.interface_id)
#            devname = self.handle.getString(2, 6)

        #    print self.handle.getDescriptor(usb.DT_STRING, 1, 20)
        except usb.USBError, err:
            print >> sys.stderr, err
            self.handle = None
            return

#        print "Seen:", devname

#        if devname != "PT-LED":
#            print >> sys.stderr, "Not adaptive device.", devname
#            self.close()
#            return 1
        return 0

    def close(self):
        if not self.handle:
            return
        try:
#            self.handle.reset()
            self.handle.releaseInterface()
        except Exception, err:
            print >> sys.stderr, err
            return 1
        finally:
            self.handle, self.device = None, None
        return 0

    def led_on(self, data):
        if not self.handle:
            return

#        data = [0, 3, 0, 1]
        try:
            self.handle.controlMsg(usb.TYPE_VENDOR|usb.RECIP_DEVICE|usb.ENDPOINT_OUT, CMD_SET, data, 0, 0, 100)
        except Exception, err:
            print >> sys.stderr, err
            raise err
        return 0

import random
import time

def main():
    dev = usb_led()
    dev.open()

    try:
#        for i in range(1000):
        while True:
            arg = [int(random.random()*10)%4, int(random.random()*10)%2]
            print arg
            dev.led_on(arg)
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    except Exception, err:
        pass
    finally:
        dev.close()

#arg = [int(x) for x in sys.argv[1:3]]
#print arg

if __name__ == "__main__":
    main()
    sys.exit(0)
