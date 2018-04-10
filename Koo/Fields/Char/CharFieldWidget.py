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

from Koo.Common import Common
from PyQt5.QtWidgets import *
from Koo.Common import Shortcuts

from Koo.Fields.TranslationDialog import *
from Koo.Fields.AbstractFieldWidget import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class CharFieldWidget(AbstractFieldWidget):
    def __init__(self, parent, view, attrs={}):
        AbstractFieldWidget.__init__(self, parent, view, attrs)

        self.widget = QLineEdit(self)
        self.widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        if 'size' in attrs:
            self.widget.setMaxLength(int(attrs['size']))
        if 'password' in attrs:
            self.widget.setEchoMode(QLineEdit.Password)

        # As there's no sense in this widget to handle focus
        # we set QLineEdit as the proxy widget. Without this
        # editable lists don't work properly.
        self.setFocusProxy(self.widget)
        self.installPopupMenu(self.widget)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.widget)

        self.scClear = QShortcut(self.widget)
        self.scClear.setKey(Shortcuts.ClearInField)
        self.scClear.setContext(Qt.WidgetShortcut)
        self.scClear.activated.connect(self.clear)

        if attrs.get('translate', False):
            pushTranslate = QToolButton(self)
            pushTranslate.setIcon(QIcon(':/images/locale.png'))
            pushTranslate.setFocusPolicy(Qt.NoFocus)
            layout.addWidget(pushTranslate)
            pushTranslate.clicked.connect(self.translate)

            self.scTranslate = QShortcut(self.widget)
            self.scTranslate.setKey(Shortcuts.SearchInField)
            self.scTranslate.setContext(Qt.WidgetShortcut)
            self.scTranslate.activated.connect(self.translate)

        self.widget.editingFinished.connect(self.store)

    def translate(self):
        if not self.record.id:
            QMessageBox.information(self, _('Translation dialog'), _(
                'You must save the resource before adding translations'))
            return
        dialog = TranslationDialog(self.record.id, self.record.group.resource, self.attrs['name'], str(
            self.widget.text()), TranslationDialog.LineEdit, self)
        if dialog.exec_() == QDialog.Accepted:
            self.setText(dialog.result)

    def storeValue(self):
        # The function might be called by 'editingFinished()' signal when no
        # record is set.
        if not self.record:
            return
        self.record.setValue(self.name, str(self.widget.text()) or False)

    def clear(self):
        self.widget.clear()
        self.widget.setToolTip('')

    def showValue(self):
        self.setText(self.record.value(self.name) or '')

    def setText(self, text):
        self.widget.setCursorPosition(0)
        self.widget.setText(text)
        self.widget.setToolTip(text)

    def setReadOnly(self, value):
        AbstractFieldWidget.setReadOnly(self, value)
        self.widget.setReadOnly(value)

    def colorWidget(self):
        return self.widget
