##############################################################################
#
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

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Koo.Common.Ui import *
from Koo.Common import Common

(GoToIdDialogUi, GoToIdDialogBase) = loadUiType(Common.uiPath('gotoid.ui'))


class GoToIdDialog(QDialog, GoToIdDialogUi):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        GoToIdDialogUi.__init__(self)
        self.setupUi(self)
        self.uiId.selectAll()

        self.pushAccept.clicked.connect(self.slotAccept)

    def slotAccept(self):
        self.result = self.uiId.value()
        self.accept()
