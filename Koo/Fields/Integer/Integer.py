##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
# Copyright (c) 2007-2008 Albert Cervera i Areny <albert@nan-tic.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Koo.Fields.AbstractFieldWidget import *
from PyQt5.QtWidgets import *
from Koo.Fields.AbstractFieldDelegate import *
from Koo.Common.Numeric import *
from Koo.Common import Shortcuts
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class IntegerFieldWidget(AbstractFieldWidget):
    def __init__(self, parent, model, attrs={}):
        AbstractFieldWidget.__init__(self, parent, model, attrs)
        self.widget = QLineEdit(self)
        self.widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.widget.setAlignment(Qt.AlignRight)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widget)

        # Shortcut
        self.scClear = QShortcut(self.widget)
        self.scClear.setKey(Shortcuts.ClearInField)
        self.scClear.setContext(Qt.WidgetShortcut)
        self.scClear.activated.connect(self.clear)

        self.widget.editingFinished.connect(self.calculate)
        self.installPopupMenu(self.widget)

    def calculate(self):
        val = textToInteger(str(self.widget.text()))
        self.setText(integerToText(val))
        self.modified()

    def value(self):
        return textToInteger(str(self.widget.text()))

    def storeValue(self):
        self.record.setValue(self.name, self.value())

    def clear(self):
        self.setText('0')

    def showValue(self):
        value = self.record.value(self.name)
        self.setText(str(value))

    def setReadOnly(self, value):
        AbstractFieldWidget.setReadOnly(self, value)
        self.widget.setReadOnly(value)

    def colorWidget(self):
        return self.widget

    def setText(self, text):
        self.widget.setCursorPosition(0)
        self.widget.setText(text)
        self.widget.setToolTip(text)


class IntegerFieldDelegate(AbstractFieldDelegate):
    def setModelData(self, editor, model, index):
        value = textToInteger(str(editor.text()))
        model.setData(index, QVariant(value), Qt.EditRole)
