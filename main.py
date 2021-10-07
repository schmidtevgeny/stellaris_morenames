#!/usr/bin/python3
from PyQt5 import QtWidgets, QtGui
import sys
import re

regex = r"\s*(\S*):\d* \"(.*)\""

def clear(test_str):
    regex = r"§\w(.*?)§!"    
    subst = "\\g<1>"
    # You can manually specify the number of replacements by changing the 4th argument
    result = re.sub(regex, subst, test_str, 0, re.MULTILINE)
    return result
        
class Widget(QtWidgets.QWidget):
    def __init__(self):
        super(Widget, self).__init__()
        self.lt = QtWidgets.QGridLayout(self)
        self.l = QtWidgets.QTextEdit()
        self.l.setFont(QtGui.QFont("Hack Nerd Font", 14))
        self.l.setWordWrapMode(True)
        self.l.setAcceptRichText(False)
        self.r = QtWidgets.QTextEdit()
        self.r.setFont(QtGui.QFont("Hack Nerd Font", 14))
        self.r.setWordWrapMode(True)
        self.r.setAcceptRichText(False)
        self.cmp = QtWidgets.QPushButton('=')
        self.cmp.clicked.connect(self.on_cmp)
        
        self.l_r = QtWidgets.QPushButton('->')
        self.r_l = QtWidgets.QPushButton('<-')
        self.lt.addWidget(self.l, 0, 0, 4, 1)
        self.lt.addWidget(self.l_r, 0, 1)
        self.lt.addWidget(self.r_l, 1, 1)
        self.lt.addWidget(self.cmp, 3, 1)
        self.lt.addWidget(self.r, 0, 2, 4, 1)
        self.l_r.clicked.connect(self.to_right)
        self.r_l.clicked.connect(self.to_left)

    def on_cmp(self):
        lstr = self.l.toPlainText()
        matches = re.finditer(regex, lstr, re.MULTILINE)
        ldata={}
        for matchNum, match in enumerate(matches, start=0):
            ldata[match.group(1)] = match.group(2)

        rstr = self.r.toPlainText()
        matches = re.finditer(regex, rstr, re.MULTILINE)
        rdata={}
        for matchNum, match in enumerate(matches, start=0):
            rdata[match.group(1)] = match.group(2)
        diff = {}
        for (i,j) in rdata.items():
            if i not in ldata:
                diff[i]=j
        for (i,j) in ldata.items():
            if i not in rdata:
                diff[i]=j
        self.r.setText("\n".join(['{}: "{}"'.format(i, j) for (i,j) in diff.items()]))


    def to_left(self):
        langdata = self.l.toPlainText()
        newlang = langdata
        matches = re.finditer(regex, langdata, re.MULTILINE)
        rdata = self.r.toPlainText().split("\n")
        
        for matchNum, match in enumerate(matches, start=0):
            if matchNum>=len(rdata):
                QtWidgets.QMessageBox.warning(self, 'errro', 'matchNum>=len(rdata)')
                return
            newlang = newlang.replace('"{}"'.format(match.group(2)), '"{}"'.format(rdata[matchNum]))
        self.l.setText(newlang)


    def to_right(self):
        langdata = self.l.toPlainText()
        self.l.setText(langdata)
        matches = re.finditer(regex, langdata, re.MULTILINE)
        rdata = []

        for matchNum, match in enumerate(matches, start=1):
            rdata.append(clear(match.group(2)))
        s = "\n".join(rdata)
        s = s + "\nTotal: {}".format(len(s))
        self.r.setText(s)
        # print(rdata)

a = QtWidgets.QApplication(sys.argv)
w = Widget()
w.show()
sys.exit(a.exec_())