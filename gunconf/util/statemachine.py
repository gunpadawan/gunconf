from logging import *
import gunconf


class StateMachine(object):

    def __init__(self, pObj, pStates, pState):
        """ """
        self._states    = pStates
        self._state     = pState
        self._obj       = pObj
        self._l         = getLogger('gunconf.StateMachine')


    def doTransition(self, pTrans):
        """ execute transition """

        self._l.debug('doTransition with state %s and trans %s'
                      % (self._state, pTrans))

        transitions = self._states[self._state]
        # retrieve name
        nSt, cb = transitions[pTrans]

        if nSt != self._state:
            self._l.info('%s -> %s' % (self._state, nSt))
            self._state = nSt

        if cb and self._obj.cb:
            self._obj.cb(pTrans, self._state)


    def addState(self, pState):
        """ add state """
        self._states[pState] = {}


    def addTransition(self, pSrcSt, pTrans, pDstSt, pCb=False):
        """ add a transition to state machine """
        srcStates = None
        if '*' == pSrcSt:
            srcStates = self._states.keys()
        else:
            srcStates = [pSrcSt]

        for srcSt in srcStates:
            self._states[srcSt][pTrans] = (pDstSt, pCb)


    def handle(self):
        # get state handler
        handler = getattr(self._obj, "state_"+self._state)
        # call handler
        return handler()

