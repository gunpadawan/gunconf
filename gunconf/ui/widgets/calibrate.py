from pgu.gui import widget
from pgu import gui
from pgu.gui.const import *
from pygame import *
import os
import gunconf

class BgdTarget(widget.Widget):

    _rct = None

    def __init__(self,value=None,**params):
        params.setdefault('focusable',False)
        widget.Widget.__init__(self,**params)
        self._oldX, self._oldY = 0, 0
        self.x, self.y = 0, 0
        self._rct = None
        self.draw = False
        self._ca = pygame.image.load(
            os.path.join(os.path.dirname(__file__),
                         "../../data/theme/res/crosshair.png"))

    def paint(self,s):
        s.fill(Color(75,75,75))
        if self.draw:
            self._drawCrossHair(s)


    def update(self,s):
        rcts = []
        if (self._oldX != self.x) or (self._oldY != self.y):
            # something has changed
            if self._rct:
                # erase old position
                pygame.draw.rect(s, Color(75,75,75), self._rct)
                rcts.append(self._rct)
            # draw new one if asked
            if self.draw:
                self._drawCrossHair(s)
                rcts.append(self._rct)

            # update positions
            self._oldX, self._oldY = self.x, self.y

        return rcts


    def _drawCrossHair(self, s):
        rct = self._ca.get_bounding_rect()
        drawRct = pygame.Rect(self.x-rct.width/2,
                                self.y-rct.height/2,
                                rct.width,
                                rct.height)
        s.blit(self._ca, drawRct)
        self._rct = drawRct


class CalibrationWnd(gui.container.Container):

    _gunPos = {'x':0, 'y':0}

    def __init__(self, pSize, pApp, **params):

        gui.container.Container.__init__(self,**params)

        self._scnW = pygame.display.Info().current_w
        self._scnH = pygame.display.Info().current_h

        self._bgd = None

        self.add(gui.Spacer(self._scnW, self._scnH), 0, 0)
        # background color
        self.setBackground()

        tbl = gui.Table(width=200, height=150)
        tbl.tr()

        ## aspect ratio
        grp = gui.Group()
        btn = gui.Radio(grp, value='4/3')
        btn.connect(CLICK, self.setBackground, True)
        tbl.td(btn)
        tbl.td(gui.Label('4/3'))

        btn = gui.Radio(grp, value='16/9')
        btn.connect(CLICK, self.setBackground, False)
        tbl.td(btn)
        tbl.td(gui.Label('16/9'))

        tbl.tr()

        # quit button
        btn = gui.Button(value='Close')
        btn.connect(CLICK, pApp.stopCal, None)
        tbl.td(btn, colspan=4)
        tbl.tr()


        self.add(tbl, (self._scnW-200)/2, self._scnH/2-75)

        self._tbl = tbl

        # set default value
        grp.value = '16/9'
        self.setBackground(False)


    def addAt(self,w,x,y,i):
        """Add a widget to the container given the position."""
        w.style.x = x
        w.style.y = y
        w.container = self
        self.widgets.insert(i, w)
        self.chsize()


    def setBackground(self, fourthird=True):
        if self._bgd:
            self.remove(self._bgd)

        w = self._scnW
        h = self._scnH
        if fourthird:
            w = h * 4 / 3
            if w > self._scnW:
                w = self._scnW
                h = w * 3 / 4
        else:
            w = h * 16 / 9
            if w > self._scnW:
                w = self._scnW
                h = w * 9 / 16

        self._bgdW = w
        self._bgdH = h
        self._bgd = BgdTarget(width=w, height=h)

        self.addAt(self._bgd, (self._scnW-w)/2, (self._scnH-h)/2, 0)


    def update(self,s):
        rcts = gui.container.Container.update(self, s)

        us = self._bgd.update(gui.surface.subsurface(s,self._bgd.rect))
        for u in us:
            rcts.append(Rect(u.x + self._bgd.rect.x,
                             u.y + self._bgd.rect.y,
                             u.w,
                             u.h))

        tblRct = self._tbl.rect
        # this should be refined to subwidgets...
        if -1 != tblRct.collidelist(rcts):
            self._tbl.paint(gui.surface.subsurface(s,self._tbl.rect))
            rcts.append(tblRct)

        return rcts


    @property
    def gunPos(self):
        return self._gunPos

    @gunPos.setter
    def gunPos(self, pos):
        # check data is valid
        if not pos or not len(pos):
            return

        update = False

        x = pos['x'] if pos.has_key('x') else None
        y = pos['y'] if pos.has_key('y') else None

        if x and x != self._gunPos['x']:
            # we have a new x
            self._gunPos['x'] = x
            # compute pointer position
            self._bgd.x = x * self._bgdW / pos['w']
            # ask for a repaint
            update = True

        if y and y != self._gunPos['y']:
            # we have a new y
            self._gunPos['y'] = y
            # compute pointer position
            self._bgd.y = y * self._bgdH / pos['h']
            # ask for a repaint
            update = True

        if update:
            self._bgd.draw = (x and x!=pos['w'])
            self.reupdate()


if __name__ == '__main__':
    # build an app with our main window

    class inApp(gui.Desktop):
        def __init__(self):
            gui.Desktop.__init__(self)
        def stopCal(self, _):
            self.quit()

        def loop(self):
            self.set_global_app()
            for e in pygame.event.get():
                if e.type == pygame.USEREVENT:
                    import random
                    self.widget.gunPos = {'x':random.randint(0,200),
                                          'y':random.randint(0,200),
                                          'w':200,
                                          'h':200}
                elif not (e.type == QUIT and self.mywindow):
                    self.event(e)

            rects = self.update(self.screen)
            pygame.display.update(rects)


    screen = pygame.display.set_mode((1280,1024),HWSURFACE)

    app = inApp()
    calWnd = CalibrationWnd((1280, 1024), app)

    pygame.time.set_timer(USEREVENT, 20)

    app.run(calWnd, screen=screen)

