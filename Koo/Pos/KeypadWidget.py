#   Copyright (C) 2008 by Albert Cervera i Areny
#   albert@nan-tic.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Koo.Common.Ui import *
from Koo.Common import Common
from .AbstractKeyboardWidget import *

(KeypadWidgetUi, KeypadWidgetBase) = loadUiType(Common.uiPath('keypad.ui'))

# @brief The KeyboardWidget class provides a virtual on-screen numeric keyboard.


class KeypadWidget(AbstractKeyboardWidget, KeypadWidgetUi):
    # @brief Creates a KeypadWidget that will send keyboard events to it's parent. It will
    # also be positioned in the screen acording to its parent coordinates.
    def __init__(self, parent):
        AbstractKeyboardWidget.__init__(self, parent)
        KeypadWidgetUi.__init__(self)
        self.setupUi(self)
        self.init()
