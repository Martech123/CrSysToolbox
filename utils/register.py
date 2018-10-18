class Register(object):
    LEN_LIST = (8, 16)

    def __init__(self, regAddr, regHex, regBin, addrLen, regLen):
        '''
        regHex:     LineEdit
        regBin:     LineEdit
        regLen:     in LEN_LIST
        regAddr:    LineEdit
        addrLen:    in LEN_LIST
        '''
        self._regHex = regHex
        self._regBin = regBin
        self._regAddr = regAddr

        if regLen not in self.LEN_LIST: raise ValueError
        if addrLen not in self.LEN_LIST: raise ValueError

        self._binLen = regLen
        self._hexLen = self._binLen / 4
        self._regMask = (1 << self._binLen) - 1
        self._binPattern = "{0:0%db}" % self._binLen
        self._hexPattern = "{0:0%dx}" % (self._binLen / 4)

        self._addrLen = addrLen / 4
        self._addrMask = (1 << addrLen) - 1

        # reg Hex
        self._regHex.setInputMask("H" * self._hexLen)
        self._regHex.setText(self._regHex.inputMask().replace("H", "0"))
        self._regHex.setPlaceholderText("Value")

        # reg Bin
        self._regBin.setInputMask(reduce(
            lambda x, y: x + " " + y,
            ["BBBB" for i in range(self._hexLen)]))
        self._regBin.setText(self._regBin.inputMask().replace("B", "0"))
        self._regBin.setPlaceholderText("Value(bin)")

        # reg Addr
        self._regAddr.setInputMask("H" * self._addrLen)
        self._regAddr.setText(self._regAddr.inputMask().replace("H", "0"))
        self._regAddr.setPlaceholderText("Addr")

    def getRegAddr(self):
        strA = self._regAddr.text()
        if len(strA) != self._addrLen:
            return None
        return int(strA, 16) & self._addrMask

    def getRegVal(self):
        strH = self._regHex.text()
        if len(strH) != self._hexLen:
            return None
        return int(strH, 16) & self._regMask

    def setRegVal(self, value):
        v = self._regMask & value
        self._regBin.setText(self._binPattern.format(v))
        self._regHex.setText(self._hexPattern.format(v))

    def regHexChanged(self):
        if self._regHex.hasFocus() is not True:
            return

        lenH = self._hexLen
        strH = self._regHex.text()
        if len(strH) <= lenH:
            strH = strH + "0" * (lenH - len(strH))
        data = int(strH, 16) & self._regMask
        self._regBin.setText(self._binPattern.format(data))

    def regBinChanged(self):
        if self._regBin.hasFocus() is not True:
            return

        strB = self._regBin.text().replace(" ", "")
        if len(strB) <= 16:
            strB = strB + "0" * (self._binLen - len(strB))
        data = int(strB, 2) & self._regMask
        self._regHex.setText(self._hexPattern.format(data))
