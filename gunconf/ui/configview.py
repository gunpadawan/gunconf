from pgu import gui

def _slChange((sl, input)):
    input.value = sl.value


def _buildSltCb(tt):
    slt = gui.Select()
    slt.add(_('Left'), 'left')
    slt.add(_('Middle'), 'middle')
    slt.add(_('Right'), 'right')
    tt.td(slt)
    chkbox = gui.Switch()
    tt.td(chkbox)
    return (slt, chkbox)


def _ckbClicked((ckb, obj)):
    obj.disabled = ckb.value


class ConfigView(object):
    def __init__(self, pSize, pApp, pDefCfg):
        tbl = gui.Table(width=pSize['w'], height=pSize['c_h'])

        ## tilt
        g = gui.Group()
        tbl2 = gui.Table()
        tbl2.tr()
        tbl2.td(gui.Label(_('Tilt / Z Correction')), colspan=2)
        tbl2.tr()
        tbl2.td(gui.Radio(g, value='off'))
        tbl2.td(gui.Label(_('Off')))
        tbl2.tr()
        tbl2.td(gui.Radio(g, value='intelligent'))
        tbl2.td(gui.Label(_('Intelligent')))
        tbl2.tr()
        tbl2.td(gui.Radio(g, value='continuous'))
        tbl2.td(gui.Label(_('Continuous')))
        self.tiltGrp = g
        tiltTbl = gui.Table(width=pSize['w']/5)
        tiltTbl.tr()
        tiltTbl.td(tbl2, style={'border':1})

        ## recoil
        recoilTbl = gui.Table(width=pSize['w']/3)
        recoilTbl.tr()
        recoilTbl.td(gui.Label(_('Recoil')))
        self.recoilSl = gui.HSlider(value=0, min=0, max=250, size=25, step=10,
                                     width=pSize['s_w'],
                                     height=pSize['s_h'])
        recoilTbl.td(self.recoilSl)
        button = gui.Button(_('Test'))
        button.connect(gui.CLICK, pApp.recoil, None)
        recoilTbl.td(button)

        ## IR gain
        irTbl = gui.Table(width=pSize['w']/3)
        irTbl.tr()
        irTbl.td(gui.Label(_('IR Gain')))
        self.irGainSl = gui.HSlider(value=1, min=1, max=5, size=10,
                                     width=pSize['s_w'],
                                     height=pSize['s_h'])
        irTbl.td(self.irGainSl)
        txt = gui.Input(size=5)
        self.irGainSl.connect(gui.CHANGE, _slChange, (self.irGainSl, txt))
        txt.focusable = False
        self.irGainSl.send(gui.CHANGE)
        irTbl.td(txt)


        ### disable auto gain
        irTbl.tr()
        irTbl.td(gui.Spacer(10,5))
        irTbl.tr()
        chkbox = gui.Switch()
        chkbox.connect(gui.CLICK, _ckbClicked, (chkbox, self.irGainSl))
        irTbl.td(chkbox)
        irTbl.td(gui.Label(_('Disable Auto Gain')), colspan=2, align=-1)
        self.autoGainSw = chkbox


        ## device ID
        devTbl = gui.Table(width=pSize['w']/4)
        devTbl.tr()
        devTbl.td(gui.Label(_('Device ID:')))
        self.devIdSlt = gui.Select()
        for x in xrange(0x1601,0x1609):
            self.devIdSlt.add('0x%x' % x, x)
        devTbl.td(self.devIdSlt)


        ## button assignments
        btnTbl = gui.Table()
        btnTbl.tr()
        btnTbl.td(gui.Label(_('Button Assignments')), colspan=5)
        btnTbl.tr()
        btnTbl.td(gui.Spacer(20,20))
        btnTbl.tr()
        btnTbl.td(gui.Label(""))
        btnTbl.td(gui.Label(_('On Screen')+"  "))
        btnTbl.td(gui.Label(_('Enable Cal')+"  "))
        btnTbl.td(gui.Label(_('Off Screen')+"  "))
        btnTbl.td(gui.Label(_('Enable Cal')+"  "))
        btnTbl.tr()
        btnTbl.td(gui.Spacer(10,5))

        ### TRIG
        btnTbl.tr()
        btnTbl.td(gui.Label(_('TRIG')+"  "))

        self.onActTrigSlt, self.onCalTrigCb = _buildSltCb(btnTbl)
        self.offActTrigSlt, self.offCalTrigCb = _buildSltCb(btnTbl)

        ### LEFT
        btnTbl.tr()
        btnTbl.td(gui.Label(_('LEFT')+"  "))

        self.onActLeftSlt, self.onCalLeftCb = _buildSltCb(btnTbl)
        self.offActLeftSlt, self.offCalLeftCb = _buildSltCb(btnTbl)

        ### RIGHT
        btnTbl.tr()
        btnTbl.td(gui.Label(_('RIGHT')+"  "))

        self.onActRightSlt, self.onCalRightCb = _buildSltCb(btnTbl)
        self.offActRightSlt, self.offCalRightCb = _buildSltCb(btnTbl)


        ## Cal Delay
        calTbl = gui.Table(width=pSize['w']/4)
        calTbl.tr()
        calTbl.td(gui.Label(_('Cal Delay (Secs)')))
        self.calDlSl = gui.HSlider(value="3", min=3, max=10, size=10,
                                    width=pSize['s_w'],
                                    height=pSize['s_h'])
        calTbl.td(gui.Spacer(10,5))
        calTbl.td(self.calDlSl)
        txt = gui.Input(size=5)
        self.calDlSl.connect(gui.CHANGE, _slChange, (self.calDlSl, txt))
        txt.focusable = False
        self.calDlSl.send(gui.CHANGE)
        calTbl.td(gui.Spacer(10,5))
        calTbl.td(txt)

        ## joystick / mouse
        self.mjGrp = gui.Group()
        jtkTbl = gui.Table(width=pSize['w']/3)
        jtkTbl.tr()
        rad = gui.Radio(self.mjGrp, value='joystick')
        # we don't support joystick yet
        rad.disabled = True
        jtkTbl.td(rad)
        jtkTbl.td(gui.Label(_('Emulate Joystick')))
        jtkTbl.td(gui.Radio(self.mjGrp, value='mouse'))
        jtkTbl.td(gui.Label(_('Emulate Mouse')))

        ## button save
        saveBtn = gui.Button(_('Save Configuration'))
        saveBtn.connect(gui.CLICK, pApp.save, None)

        dcntBtn = gui.Button(_('Disconnect'))
        dcntBtn.connect(gui.CLICK, pApp.disconnect, None)

        ## button set defaults
        defBtn = gui.Button(_('Set Defaults'))
        defBtn.connect(gui.CLICK, self.setConfig, pDefCfg)

        # assemble window
        tbl.tr()
        tbl.td(tiltTbl)
        tbl.td(btnTbl)
        tbl.tr()
        tbl.td(recoilTbl)
        tbl.td(calTbl)
        tbl.tr()
        tbl.td(irTbl)
        tbl.td(jtkTbl)
        tbl.tr()
        tbl.td(devTbl)
        tbl.tr()
        tbl.td(defBtn)
        tbl.td(saveBtn)
        tbl.tr()
        tbl.td(dcntBtn, colspan=2)

        # Configuration
        self.widget = tbl


    def setConfig(self, config):
        """ set configuration to use """
        self.irGainSl.value         = config['irGain']
        self.calDlSl.value          = config['calDelay']
        self.recoilSl.value         = config['recoil']
        self.mjGrp.value        = 'joystick' if config['joystick'] else 'mouse'
        self.tiltGrp.value          = config['tilt']

        self.offCalTrigCb.value     = config['offCalTrig']
        self.onCalTrigCb.value      = config['onCalTrig']
        self.offCalLeftCb.value     = config['offCalLeft']
        self.onCalLeftCb.value      = config['onCalLeft']
        self.offCalRightCb.value    = config['offCalRight']
        self.onCalRightCb.value     = config['onCalRight']

        self.onActTrigSlt.value     = config['onActTrig']
        self.offActTrigSlt.value    = config['offActTrig']
        self.onActLeftSlt.value     = config['onActLeft']
        self.offActLeftSlt.value    = config['offActLeft']
        self.onActRightSlt.value    = config['onActRight']
        self.offActRightSlt.value   = config['offActRight']

        self.autoGainSw.value       = not config['autoGain']
        self.devIdSlt.value         = config['idProduct']


    def getConfig(self):
        """ get configuration """
        config = {}
        config['irGain']        = self.irGainSl.value
        config['calDelay']      = self.calDlSl.value
        config['recoil']        = self.recoilSl.value
        config['joystick']      = (self.mjGrp.value == 'joystick')
        config['tilt']          = self.tiltGrp.value
        config['offCalTrig']    = self.offCalTrigCb.value
        config['onCalTrig']     = self.onCalTrigCb.value
        config['offCalLeft']    = self.offCalLeftCb.value
        config['onCalLeft']     = self.onCalLeftCb.value
        config['offCalRight']   = self.offCalRightCb.value
        config['onCalRight']    = self.onCalRightCb.value

        config['offActTrig']    = self.offActTrigSlt.value
        config['onActTrig']     = self.onActTrigSlt.value
        config['offActLeft']    = self.offActLeftSlt.value
        config['onActLeft']     = self.onActLeftSlt.value
        config['offACtRight']   = self.offActRightSlt.value
        config['onActRight']    = self.onActRightSlt.value

        config['autoGain']      = not self.autoGainSw.value
        config['idProduct']     = self.devIdSlt.value

        return config

