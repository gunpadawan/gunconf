import evdev
from evdev import ecodes
import time
from logging import *
import gunconf


convert = { ecodes.ABS_X: 'x',
           ecodes.ABS_Y : 'y',
           ecodes.BTN_MOUSE : 'left',
           ecodes.BTN_RIGHT : 'right',
           ecodes.BTN_MIDDLE : 'middle'}


class AbsMouseManager(object):

    def __init__(self):
        self._devs  = {}
        self._l     = getLogger('gunconf.drivers.AbsMouseManager')

    def scan(self, pVendor=None):
        """ scan devices with absolute coordinates """
        self._devs = {}
        for name in evdev.list_devices():
            dev = evdev.InputDevice(name)
            if dev.capabilities().has_key(ecodes.EV_ABS):
                if not pVendor or pVendor == dev.info.vendor:
                    self._devs[name] = dev

        self._l.info("found %d devices" % (len(self._devs)))

        return len(self._devs)


    def read(self, name=None):

        devs = None
        if name:
            devs =  [self._devs[name]]
        else:
            devs = self._devs.values()

        for dev in devs:
            try:
                events = dev.read()
                for event in events:
                    if event.type == evdev.ecodes.EV_MSC:
                        self._l.info('read: event found for %s', dev.fn)
                        return (dev.fn, event)
            except IOError:
                pass

        self._l.debug('read: no event found')
        return (None, None)


    def update(self, name):
        dct = {}
        try:
            events = self._devs[name].read()
            for event in events:
                if (ecodes.EV_ABS == event.type and \
                        event.code in [ecodes.ABS_X, ecodes.ABS_Y]) or \
                        (ecodes.EV_KEY == event.type and \
                         event.code in [ecodes.BTN_MOUSE,
                                        ecodes.BTN_RIGHT,
                                        ecodes.BTN_MIDDLE]):
                    dct[convert[event.code]] = event.value
        except IOError:
            pass

        if len(dct):
            cap = self._devs[name].capabilities()
            dct['w'] = cap[ecodes.EV_ABS][ecodes.ABS_X][1].max
            dct['h'] = cap[ecodes.EV_ABS][ecodes.ABS_Y][1].max

        self._l.debug("update %s", str(dct))
        return dct


if __name__ == '__main__':

    getLogger().setLevel(INFO)

    mouseManager = AbsMouseManager()

    mouseManager.scan()
    name = None
    print mouseManager._devs

    # connect to the first mouse on which something happen
    while True:
        name, _ = mouseManager.read()
        if name:
            break
        time.sleep(1)

    # display new position
    while True:
        status = mouseManager.update(name)
        if status:
            print status
        time.sleep(1.0/50)
