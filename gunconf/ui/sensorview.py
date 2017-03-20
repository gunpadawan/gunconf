
from pgu import gui
from gunconf.ui.widgets.irtest import IrTest
import textwrap

class SensorView(object):
    def __init__(self, pSize, pApp):
        tbl = gui.Table(width=pSize['w'], height=pSize['c_h'])

        # text on the left
        tbl2 = gui.Table()
        tbl2.tr()
        txt = _("To ckeck operation\n"
                "Aim gun sight at monitor\n"
                "Move gun within monitor boundary.\n"
                "Ensure IR point is visible\n"
                "to the gun when aimed\n"
                "at all areas of the screen.")

        lines = txt.split("\n")
        for line in lines:
            tbl2.tr()
            tbl2.td(gui.Label(str(line)))

        txtTbl = gui.Table(height=pSize['ir_h'])
        txtTbl.tr()
        txtTbl.td(tbl2, style={'border':1})

        # legend
        tbl2 = gui.Table()
        tbl2.tr()
        tbl2.td(gui.Color(width=30,height=30, value=(255,0,0)))
        tbl2.td(gui.Label("   "+_('IR Good')), align=-1)
        tbl2.tr()
        tbl2.td(gui.Spacer(10,10))
        tbl2.tr()
        tbl2.td(gui.Color(width=30,height=30, value=(255,165,0)))
        tbl2.td(gui.Label("   "+_('IR Good but faint')), align=-1)
        tbl2.tr()
        tbl2.td(gui.Spacer(10,10))
        tbl2.tr()
        tbl2.td(gui.Color(width=30,height=30, value=(0,0,0)))
        tbl2.td(gui.Label("   "+_('IR Not visible')), align=-1)

        txtTbl.tr()
        txtTbl.td(gui.Spacer(10,10))
        txtTbl.tr()
        txtTbl.td(tbl2, style={'border':1})


        # test area
        self.tstArea = IrTest(width=pSize['ir_w'], height=pSize['ir_h'])

        # calibrate button
        btn = gui.Button(_('Calibrate'))
        btn.connect(gui.CLICK, pApp.startCal, None)

        tbl.tr()
        tbl.td(txtTbl)
        tbl.td(self.tstArea)

        tbl.tr()
        tbl.td(btn, colspan=2)

        self.widget = tbl


