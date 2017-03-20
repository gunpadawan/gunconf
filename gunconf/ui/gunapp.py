import pygame
from pygame.locals import *
from pgu import gui
from gunconf.ui.widgets.calibrate import CalibrationWnd
from gunconf.ui.configview import ConfigView
from gunconf.ui.sensorview import SensorView
import os
import logging
import gunconf


########################################################
#############       constants       ####################
########################################################

sizeSD = {'w'   : 640,
          'm_h' : 40,
          'm_w' : (640-20)/2,
          'c_h' : 480-150,
          's_w' : 80,
          's_h' : 20,
          'ir_w': 300,
          'ir_h': 200}


sizeHD = {'w'   : 1280,
          'm_h' : 40,
          'm_w' : (1280-20)/2,
          'c_h' : 720-150,
          's_w' : 180,
          's_h' : 20,
          'ir_w': 800,
          'ir_h': 450}


defaultCfg = {'irGain'      : 1,
              'autoGain'    : False,
              'calDelay'    : 5,
              'recoil'      : 100,
              'joystick'    : False,
              'tilt'        : 'continuous',
              'offActTrig'  : 'left',
              'onActTrig'   : 'left',
              'offActLeft'  : 'middle',
              'onActLeft'   : 'middle',
              'offActRight' : 'right',
              'onActRight'  : 'right',
              'onCalTrig'   : False,
              'offCalTrig'  : False,
              'onCalLeft'   : True,
              'offCalLeft'  : True,
              'onCalRight'  : True,
              'offCalRight' : True,
              'idProduct'   : 0x1601}


########################################################
#################   top widget  ########################
########################################################

class GunApp(gui.Desktop):
    def __init__(self, width, height):
        """ build the application givent it's width and height """

        # set logger
        self._l     = logging.getLogger('gunconf.ui.gunapp')

        tmLb        = 'HD'
        self._size  = sizeHD

        # allocate screen
        if not width or not height:
            self._screen = pygame.display.set_mode((0,0),FULLSCREEN)
        else:
            self._screen = pygame.display.set_mode((width,height),SWSURFACE)

        # disable mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_blocked(pygame.MOUSEMOTION)
        pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
        pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)

        # init joysticks
        pygame.joystick.init()
        for x in range(pygame.joystick.get_count()):
            pygame.joystick.Joystick(x).init()

        # rollback to SD res if needed
        if 720 >= pygame.display.Info().current_h:
            self._size = sizeSD
            tmLb = 'SD'

        # create app object
        theme=gui.Theme(os.path.join(os.path.dirname(__file__),
                                     "../data/theme/%s"%(tmLb,)))
        gui.Desktop.__init__(self, theme=theme)
        self._ctrl          = None
        self._waitNbScan    = 0

        self.connect(gui.QUIT,self.quit,None)

        # init UI
        self._initUi()


    def _initUi(self):
        """ init the different elements of the ui """

        self._grp = gui.Group()
        self._grp.connect(gui.CHANGE,self._chgTab)

        # top widget
        self._widget = gui.Table()
        # tabs
        self._tabs = gui.Table(width=self._size['w'])
        self._widget.td(self._tabs)
        self._widget.tr()
        self._widget.td(gui.Spacer(10,10))

        # Config view
        self._cv = ConfigView(self._size, self, defaultCfg)
        b = gui.Tool(self._grp, gui.Label(_('Configuration')),
                     self._cv.widget,
                     height=self._size['m_h'], width=self._size['m_w'])
        self._tabs.td(b, align=-1)
        self._cfgBtn = b

        # Sensor view
        self._sv = SensorView(self._size, self)
        b = gui.Tool(self._grp,gui.Label(_('Sensor View Check')),
                     self._sv.widget,
                     height=self._size['m_h'], width=self._size['m_w'])
        self._tabs.td(b, align=1)

        # Connection table
        self._widget.tr()
        self._conTb = gui.Table(width=self._size['w'], height=self._size['c_h'])
        self._conTb.tr()
        self._infoLb = gui.Label(_('Pull Gun Trigger to start configuration'))
        self._conTb.td(self._infoLb)
        self._conTb.tr()
        self._conLb = (gui.Label('-- 0 '+_('device(s) connected')+' --'))
        self._conTb.td(self._conLb)


        box = gui.ScrollArea(self._conTb)
        self._widget.td(box,style={'border':1},colspan=4)
        self._tab = box

        # Status bar
        self._widget.tr()

        tt2 = gui.Table(width=self._size['w'])
        tt2.tr()

        self._devIdLb = gui.Label('')
        self._firmLb = gui.Label('')

        tt2.td(self._devIdLb)
        tt2.td(self._firmLb, align=1)
        tt2.tr()
        self._quitBn = gui.Button(_("Quit"))
        self._quitBn.connect(gui.CLICK, self.quit, None)
        tt2.td(self._quitBn, colspan=2)
        self._widget.td(tt2)

        # Calibration window
        self._calWn = CalibrationWnd(self._size, self)


    def setCtrl(self, pCtrl):
        """ set controler """
        self._ctrl = pCtrl


    ########################################################
    ##############      UI callbacks    ####################
    ########################################################

    def disconnect(self, _=None):
        """ disconnect gun """
        self._ctrl.disconnect()


    def quit(self,value=None):
        """ quit application """
        if self._ctrl:
            self._ctrl.stop()
        gui.Desktop.quit(self)


    def save(self, _):
        """ save configuration """
        # retrieve controler configuration
        config = self._ctrl.get('config')
        # update it with configuration from configuration view
        config.update(self._cv.getConfig())
        # set updated configuration
        self._ctrl.set('config', config)
        # adk controler to configure gun
        self._ctrl.configure()

        # TODO: disable commands


    def startCal(self, _):
        """ open calibration window """
        # start calibration
        self._ctrl.calibrate()
        # open wnd
        self._calWn.open()


    def stopCal(self, _):
        """ close calibration window """
        self._calWn.close()
        # restart irtest
        self._ctrl.irtest()


    def recoil(self, _):
        """ test recoil """
        self._ctrl.recoil()


    def disconnecting(self, pWaitForReboot=False):
        """ set UI in disconnecting state """
        # set text
        major = _('Gun is disconnected')
        minor = ''
        if pWaitForReboot:
            minor = _('Waiting for reboot...')

        self._setInfo(major, minor)


    def _chgTab(self):
        """ change active tab """
        if self._tab.widget == self._grp.value:
            return

        # handle dyndata request
        if self._sv.widget == self._tab.widget:
            # end irtesting
            self._ctrl.irtested()
        elif self._sv.widget == self._grp.value:
            # enter irtesting
            self._ctrl.irtest()

        # update active tab
        self._tab.widget = self._grp.value


    def _waitForCon(self, nbDev):
        """ set UI in waiting for connection state """
        self._setInfo(_('Pull Gun Trigger to start configuration'),
                      ('-- %d ' % nbDev)+_('device(s) connected')+' --')


    def _updateNeeded(self):
        """ display that an update is needed """
        self._setInfo(_('A Firmware update is required'),
                      _('you need the windows utility to do it...'))
        # disconnect gun
        self._waitNbScan = 90
        self.disconnect()


    def _setInfo(self, pMajor=None, pMinor=None):
        """ display info to user and deactivate other controls """
        # set text
        if pMajor is not None:
            self._infoLb.value = pMajor
        if pMinor is not None:
            self._conLb.value = pMinor
        # deactivate all buttons
        self._tabs.disabled = True
        self._firmLb.value = ''
        self._quitBn.focus()

        self._tab.widget = self._conTb


    def _configuring(self, config):
        """ set device to use """
        # check version
        version = config['version']
        if version[0]<gunconf.aimtrak_version_info[0] or \
                version[1]<gunconf.aimtrak_version_info[1]:
            # old firmware, warn and disconnect
            self._updateNeeded()
            return

        # we have the device name now
        #activate buttons
        self._tabs.disabled = False
        self._tab.widget = self._cv.widget
        self._cfgBtn.focus()

        self._cv.setConfig(config)

        self._firmLb.value = _('Firmware version')+': %d.%d' % config['version']


    def _ctrlEvent(self, pTrans, pState):
        """ receive event from controler """

        # scanning
        if 'scan'==pTrans and 'scanning'==pState:
            if not self._waitNbScan:
                nbDevs = self._ctrl.get('nbDevs')
                if nbDevs:
                    # update nb connections
                    self._waitForCon(nbDevs)
                    # ask controler to wait for connection
                    self._ctrl.connect()
            else:
                self._waitNbScan -= 1
        # loading
        elif 'connected'==pTrans and 'loading'==pState:
            # update user
            self._setInfo(_('Gun detected, loading configuration...'))
        # loading complete
        elif 'loaded'==pTrans and 'waiting'==pState:
            # set config panel
            self._configuring(self._ctrl.get('config'))
        elif 'irtest'==pTrans and 'irtesting'==pState:
            # forward event to sensorview
            self._sv.tstArea.value = self._ctrl.get('dynData')
        elif 'calibrate'==pTrans and 'calibrating'==pState:
            # forward event to widget
            self._calWn.gunPos = self._ctrl.get('gunPos')
        elif 'configured'==pTrans and 'waiting'==pState:
            print "TODO: restore controls"
        elif 'reboot'==pTrans and 'disconnecting'==pState:
            self.disconnecting(True)
            # wait 15 scans (for the device to reboot)
            self._waitNbScan = 15
        elif 'disconnected'==pTrans and 'scanning'==pState:
            if not self._waitNbScan:
                self.disconnecting(False)
        else:
            self._l.info("received transition %s-->%s" % (pTrans, pState))


##############################
#####   ugly things here #####
##############################

    def ctrlCb(self, pTrans, pState):
        """ callback from controler """
        # callback is received from controler thread
        # we need to forward to UI thread
        params = {'trans': pTrans, 'state': pState}
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, params))


    def run(self):
        self._waitForCon(0)
        gui.Desktop.run(self, screen=self._screen, widget=self._widget)


    def loop(self):
        """Performs one iteration of the PGU application loop, which
        processes events and update the pygame display."""
        self.set_global_app()

        for e in pygame.event.get():
            if e.type == pygame.USEREVENT:
                self._ctrlEvent(e.trans, e.state)
            elif not (e.type == QUIT and self.mywindow):
                # overwrite event if joystick event
                params = {'mod':0, 'unicode':0, 'key': K_SPACE}
                if pygame.JOYBUTTONDOWN == e.type:
                    e = pygame.event.Event(pygame.KEYDOWN, params)
                if pygame.JOYBUTTONUP == e.type:
                    e = pygame.event.Event(pygame.KEYUP, params)
                elif pygame.JOYHATMOTION == e.type:
                    key = None
                    if e.value   == (0, -1) : key = K_DOWN
                    elif e.value == (0, 1)  : key = K_UP
                    elif e.value == (-1, 0) : key = K_LEFT
                    elif e.value == (1, 0)  : key = K_RIGHT
                    if key:
                        params['key'] = key
                        e = pygame.event.Event(pygame.KEYDOWN, params)

                self.event(e)

        rects = self.update(self.screen)
        pygame.display.update(rects)


