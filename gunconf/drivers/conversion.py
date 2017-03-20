def action_from_value(pValue):
    if 0x98 == pValue:
        return 'left'
    if 0x99 == pValue:
        return 'right'
    if 0x9A == pValue:
        return 'middle'
    return None


def action_to_value(pAction):
    if 'left'==pAction:
        return 0x98
    if 'right'==pAction:
        return 0x99
    if 'middle'==pAction:
        return 0x9A
    return None


def tilt_from_value(pValue):
    val = pValue&0x3
    if 0x2 == val:
        return 'continuous'
    if 0x1 == val:
        return 'intelligent'
    return 'off'


def tilt_to_value(pCnf, pValue):
    val = pValue & 0xFC

    if 'continuous'==pCnf:
        return val | 0x2
    if 'intelligent'==pCnf:
        return val | 0x1
    return val


def version_from_value(pValue):
    if 0x90 < pValue:
        return (0x9, pValue-0x90)
    if 0x80 < pValue:
        return (0x8, pValue-0x80)
    return (0x1, pValue-0x10)


def ir_from_value(pValue):
    if 0x1 == pValue:
        return 'faint'
    if 0xF == pValue:
        return 'notVisible'
    if 0x1 < pValue < 0xF:
        return 'good'


def config_from_buffer(pBuf):
    """ parse config from buffer """
    cnf = {}
    # calibration on buttons
    cnf['onCalTrig'] = ((pBuf[11] & 0x1) != 0)
    cnf['onCalLeft'] = ((pBuf[11] & 0x2) != 0)
    cnf['onCalRight'] = ((pBuf[11] & 0x4) != 0)
    cnf['offCalTrig'] = ((pBuf[19] & 0x1) != 0)
    cnf['offCalLeft'] = ((pBuf[19] & 0x2) != 0)
    cnf['offCalRight'] = ((pBuf[19] & 0x4) != 0)
    cnf['calDelay'] = pBuf[21]

    # actions on buttons
    cnf['offActTrig']   = action_from_value(pBuf[12])
    cnf['offActLeft']   = action_from_value(pBuf[13])
    cnf['offActRight']  = action_from_value(pBuf[14])
    cnf['onActTrig']    = action_from_value(pBuf[4])
    cnf['onActLeft']    = action_from_value(pBuf[5])
    cnf['onActRight']   = action_from_value(pBuf[6])

    cnf['joystick']     = ((pBuf[22] & 0x10) != 0)

    cnf['recoil']       = pBuf[24]

    cnf['tilt']         = tilt_from_value(pBuf[22])

    cnf['irGain']       = pBuf[20]
    cnf['autoGain']     = ((pBuf[22] & 0x8) == 0)
    cnf['version']      = version_from_value(pBuf[23])

    return cnf


def config_to_buffer(pCnf, pBuf):
    """ parse config from buffer """

    cnf = {}
    # calibration on buttons
    pBuf[11] = (pBuf[11] | 0x1) if pCnf['onCalTrig'] else (pBuf[11] & 0xFE)
    pBuf[11] = (pBuf[11] | 0x2) if pCnf['onCalLeft'] else (pBuf[11] & 0xFD)
    pBuf[11] = (pBuf[11] | 0x4) if pCnf['onCalRight'] else (pBuf[11] & 0xFB)
    pBuf[19] = (pBuf[19] | 0x1) if pCnf['offCalTrig'] else (pBuf[19] & 0xFE)
    pBuf[19] = (pBuf[19] | 0x2) if pCnf['offCalLeft'] else (pBuf[19] & 0xFD)
    pBuf[19] = (pBuf[19] | 0x4) if pCnf['offCalRight'] else (pBuf[19] & 0xFB)
    pBuf[21] = pCnf['calDelay']

    # actions on buttons
    pBuf[12] = action_to_value(pCnf['offActTrig'])
    pBuf[13] = action_to_value(pCnf['offActLeft'])
    pBuf[14] = action_to_value(pCnf['offActRight'])
    pBuf[4]  = action_to_value(pCnf['onActTrig'])
    pBuf[5]  = action_to_value(pCnf['onActLeft'])
    pBuf[6]  = action_to_value(pCnf['onActRight'])

    pBuf[22] = (pBuf[22] | 0x10) if pCnf['joystick'] else (pBuf[22] & 0xEF)

    pBuf[24] = pCnf['recoil']

    pBuf[22] = tilt_to_value(pCnf['tilt'], pBuf[22])

    pBuf[20] = pCnf['irGain']
    pBuf[22] = (pBuf[22] | 0x8) if not pCnf['autoGain'] else (pBuf[22] & 0xF7)

    return pBuf


def dyn_data_from_buffer(pBuffer):
    """ parse dynamic data from buffer """
    data = {}
    data['x'] = pBuffer[0] << 8 | pBuffer[1]
    data['y'] = pBuffer[2] << 8 | pBuffer[3]
    data['ir'] = ir_from_value(pBuffer[24])

    return data
