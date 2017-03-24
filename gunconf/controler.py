#from gunconf import mouses
from threading import *
import time
from drivers.mouse import AbsMouseManager
from drivers.aimtrak import Aimtrak
import pyudev
from collections import defaultdict
from logging import *
import gunconf
from gunconf.util.statemachine import StateMachine


gStateTrans  = {'scanning' :      {'connect': ('connecting', False), \
                                 'scan': ('scanning', True) \
                                 }, \
                \
               'connecting' :   {'connected': ('loading', True), \
                                 'connect': ('connecting', False) \
                                 }, \
                \
               'loading' :      {'loaded': ('waiting', True) \
                                 }, \
                \
               'waiting' :      {'wait': ('waiting', False), \
                                 'calibrate': ('calibrating', False), \
                                 'irtest': ('irtesting', False),\
                                 'configure': ('configuring', False),\
                                 'recoil': ('recoiling', False)\
                                 }, \
                \
               'configuring' :  {'configured': ('waiting', True), \
                                 'reboot': ('disconnecting', True), \
                                 }, \
                \
               'calibrating' :  {'calibrate': ('calibrating', True), \
                                 'calibrated': ('waiting', False), \
                                 'irtest': ('irtesting', False)\
                                 }, \
                \
               'irtesting' :    {'irtest': ('irtesting', True), \
                                 'irtested': ('waiting', False), \
                                 'calibrate': ('calibrating', False) \
                                 }, \
                \
               'recoiling' :    {'recoiled': ('waiting', True) \
                                 }, \
                 \
                'inerror' :     {'disconnected': ('scanning', True) \
                                  }, \
                \
                'disconnecting': {'disconnected': ('scanning', True) \
                                  } \
              }



class Controler(Thread):
    def __init__(self):
        Thread.__init__(self)

        # init state machine
        self._machine   = StateMachine(self, gStateTrans, 'scanning')
        # add valid transition for all states
        self._machine.addTransition('*', 'disconnect', 'disconnecting', True)
        self._machine.addTransition('*', 'error', 'inerror', True)

        # init mouse manager
        self._mouses    = AbsMouseManager()
        # init thread sync objects
        self._lock      = Lock()
        self._stop      = Event()
        # init logger
        self._l         = getLogger('gunconf.Controler')

        # callback
        self.cb         = None

        # add 'session' variables
        self._infos     = defaultdict(lambda:None)
        self._toRead    = []
        self._gun       = None


    def _reset(self):
        if self._gun:
            self._gun.close()

        self._gun       = None
        self._toRead[:] = []

        with self._lock:
            self._infos.clear()


    def transit(self, pTransit):
        self.set('override', pTransit)


    def setCb(self, pCb):
        """ set callback, must be called before start() """
        self.cb = pCb


    def run(self):
        """ main loop """
        while not self._stop.isSet():
            # handle state
            trans = self._machine.handle()

            # is transition overriden?
            override = self.get('override', True)
            if override:
                trans = override
                self.set('override', None)

            self._machine.doTransition(trans)


    def stop(self):
        """ stop thread """
        self._stop.set()
        self.join()


    ######################################################
    ##########      thread safe functions       ##########
    ######################################################

    def get(self, pAttr, pReset=False):
        ret = None
        with self._lock:
            ret = self._infos[pAttr]
            if pReset:
                self._infos[pAttr] = None
            return ret


    def set(self, pAttr, pValue):
        # values SHALL not be modified after being set
        with self._lock:
            self._infos[pAttr] = pValue


    ######################################################
    ##########      state machine states        ##########
    ######################################################

    def state_scanning(self):
        self._evdevs = self._mouses.scan(Aimtrak.vendorId)
        # aimtrak has 2 input interfaces per device: --> /2
        self.set('nbDevs', len(self._evdevs)/2)
        time.sleep(0.1)
        return 'scan'


    def state_connecting(self):
        name , _ = self._mouses.read()
        if not name:
            time.sleep(1.0/50)
            return 'connect'

        # append device to read list
        self._toRead.append(name)
        return 'connected'


    def state_loading(self):
        """ connect to gun and retrieve configuration """
        # get usb id and address using udev
        name = self._toRead[0] # we have only 1 device so far
        busId, address = self._parentInfo(name)

        # now let's find the other input device
        for oNm in self._evdevs:
            if oNm is not name:
                oBusId, oAddress = self._parentInfo(oNm)
                if oBusId == busId and oAddress == address:
                    self._toRead.append(oNm)
                    break

        self._l.info('input device to read are: %s', self._toRead)

        self._gun   = Aimtrak(busId, address)
        cnf         = self._gun.getConfig()
        self.set('config', cnf)

        self._l.info('gun configuration is: %s', cnf)

        return 'loaded'


    def state_waiting(self):
        time.sleep(0.1)
        return 'wait'


    def state_configuring(self):
        cnf = self.get('config')
        if self._gun.setConfig(cnf):
            return 'reboot'
        else:
            return 'configured'


    def state_recoiling(self):
        """ test recoil """
        # store current value
        cnf = self._gun.getConfig()
        oldVal = cnf['recoil']

        # set value to test
        cnf['recoil'] = self.get('recoil')
        self._gun.setConfig(cnf)

        # ask for recoil
        self._gun.recoil()

        # restore old value
        cnf['recoil'] = oldVal
        self._gun.setConfig(cnf)

        return 'recoiled'


    def state_irtesting(self):
        """ we are testing IR reception, retrieve dyn data """
        try:
            data = self._gun.getDynData()
            self.set('dynData', data)
            self._l.debug('got dynData: %s', data)
            #return 'irtest'
        except Exception as e:
            self._l.error("can't receive dynData \"%s\"", e)
        return 'irtest'
            #return 'error'


    def state_calibrating(self):
        """ retrieve mouse position """

        for nm in self._toRead:
            pos = self._mouses.update(nm)
            if len(pos):
                self.set('gunPos', pos)
                self._l.debug('gun controls : %s', pos)

        time.sleep(1.0/50)
        return 'calibrate'


    def state_disconnecting(self):
        """ disconnect from gun """
        self._reset()
        return 'disconnected'


    def state_inerror(self):
        return self.state_disconnecting()


    def __getattr__(self, name):
        """ provide 'functions' for a few transitions names """
        if name in ('connect', 'irtest', 'irtested', 'disconnect', 'calibrate',
                    'configure', 'recoil'):
            return lambda : self.transit(name)
        raise AttributeError


    def _parentInfo(self, name):
        """ return usb info of device """
        udev        = pyudev.Context()
        dev         = pyudev.Device.from_device_file(udev, name)
        parent      = dev.find_parent('usb','usb_device')

        busId       = int(parent['BUSNUM'])
        address     = int(parent['DEVNUM'])

        return (busId, address)


if __name__ == '__main__':

    getLogger('gunconf.Controler').setLevel(DEBUG)
    #getLogger('gunconf.drivers.Aimtrak').setLevel(DEBUG)
    #getLogger('gunconf.drivers.AbsMouseManager').setLevel(DEBUG)

    class unittest(object):
        def __init__(self, pCont):
            self._cont      = pCont
            self._counter   = 0
            self.loop       = 500

        def cb(self, trans, state):
            if 'irtesting'==state:
                self._counter+=1
                if not (self._counter % self.loop):
                    controler.transit('irtested')
                print "dyndata ", self._cont.get('dynData')
            elif 'loaded'==trans:
                while True:
                    controler.state_calibrating()
                    controler.state_irtesting()
            else:
                print "callback for %s->%s" % (trans, state)

    # init controler
    controler = Controler()

    # init inner helper class
    test = unittest(controler)

    # set callback
    controler.setCb(test.cb)

    # start controler
    controler.start()

    time.sleep(1)
    # change to connect
    controler.transit('connect')

    import IPython; IPython.embed() # XXX BREAKPOINT


    # exit gracefully
    controler.stop()
