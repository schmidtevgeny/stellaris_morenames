#!/usr/bin/python3
from PyQt5 import QtWidgets
import sys
import re

regex = r"\s*(\S*): \"(.*)\""

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
        self.r = QtWidgets.QTextEdit()
        self.l_r = QtWidgets.QPushButton('->')
        self.r_l = QtWidgets.QPushButton('<-')
        self.lt.addWidget(self.l, 0, 0, 3, 1)
        self.lt.addWidget(self.l_r, 0, 1)
        self.lt.addWidget(self.r_l, 1, 1)
        self.lt.addWidget(self.r, 0, 2, 3, 1)
        self.l_r.clicked.connect(self.to_right)
        self.r_l.clicked.connect(self.to_left)


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
        matches = re.finditer(regex, langdata, re.MULTILINE)
        rdata = []

        for matchNum, match in enumerate(matches, start=1):
            rdata.append(clear(match.group(2)))
        s = "\n".join(rdata)
        s = s + "\nTotal: {}".format(len(s))
        self.r.setText(s)
        print(rdata)

a = QtWidgets.QApplication(sys.argv)
w = Widget()
w.show()
sys.exit(a.exec_())