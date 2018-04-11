##############################################################################
#
# Copyright (c) 2007-2011 Albert Cervera i Areny <albert@nan-tic.com>
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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Koo import Rpc

# @brief The ToolBar class is a widget (which inherits QToolBar) and is used
# as the toolbar in forms.
#
# The Toolbar will have Vertical orientation and ToolButtonTextBesideIcon.


class ToolBar(QToolBar):
    # @brief Creates a new ToolBar instance.
    def __init__(self, parent=None):
        QToolBar.__init__(self, parent)
        self.setOrientation(Qt.Vertical)
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.loaded = False

    # @brief Initializes the toolbar with a list of Action objects.
    #
    # Note that it automatically adds a separator between actions of different types
    # such as between 'print' and 'action'. This function can only be called once.
    # Calling this function more times won't do anything.
    def setup(self, actions):
        if self.loaded:
            return
        self.loaded = True
        last = None
        for action in actions:
            if action.type() == 'plugin':
                continue
            if last and last != action.type():
                self.addSeparator()
            last = action.type()

            # Create a QToolButton and then add it with addWidget() instead of
            # directly using addAction() because this way buttons are left aligned
            # which looks better.
            button = QToolButton(self)
            button.setDefaultAction(action)
            button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            button.setAutoRaise(True)
            button.setText(self.wordWrap(unicode(button.text()), 25))

            self.addWidget(button)

    def wordWrap(self, text, size):
        lines = []
        currentLine = []
        currentLength = 0
        for word in text.split(' '):
            if currentLine and currentLength + len(word) + 1 >= size:
                lines.append(' '.join(currentLine))
                currentLine = []
                currentLength = 0
            currentLine.append(word)
            currentLength += len(word)
        lines.append(' '.join(currentLine))
        return '\n'.join(lines)


# vim:noexpandtab:smartindent:tabstop=8:softtabstop=8:shiftwidth=8:
