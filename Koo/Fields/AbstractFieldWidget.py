##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#					Fabien Pinckaers <fp@tiny.Be>
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

import os
import re
import tempfile

from Koo import Rpc
from Koo.Common import Api
from Koo.Common import Help
from Koo.Common import Common
from Koo.Common.Settings import *
from FieldPreferencesDialog import *

from PyQt4.QtGui import *
from PyQt4.QtCore import *


# @brief AbstractFieldWidget is the base class for all field widgets in Koo.
# In order to create a new field widget, that is: a widget that appears in a
# auto-generated form you need to inherit from this class and implement some
# of it's functions.
#
# The Widget handles a field from a record. You can access the record
# using the property 'record' and the field name using the property 'name'.
#
class AbstractFieldWidget(QWidget):

    # @brief Creates a new AbstractFieldWidget and receives the following parameters
    #  parent:     The QWidget parent of this QWidget
    #  view:       Holds the reference to the view the widget is in
    #  attributes: Holds some extra attributes such as read-only and others
    def __init__(self, parent, view, attributes):
        QWidget.__init__(self, parent)

        self.attrs = attributes
        self.view = view

        self._isInitialized = False
        self._isUpToDate = False

        # Required and readonly attributes are not directly linked to
        # the field states because a widget might not have a record
        # assigned. Also updating the attribute directly in the fields
        # can cause some problems with stateAttributes.
        self._required = self.attrs.get(
            'required', False) not in ('False', '0', False)
        self._readOnly = self.attrs.get(
            'readonly', False) not in ('False', '0', False)

        self.extraAttributes = eval(self.attrs.get('use', '{}'))

        # Find Koo specific attributes that OpenObject's Relax NG doesn't allow
        self.setStyleSheet(self.extraAttributes.get('stylesheet', ''))

        self.defaultReadOnly = self._readOnly
        self.defaultMenuEntries = [
            (_('Set to default value'), self.setToDefault, 1),
        ]
        # As currently slotSetDefault needs view to be set we use it
        # only in form views.
        if self.view:
            self.defaultMenuEntries.append(
                (_('Set as default value'), self.setAsDefault, 1))

        # self.name holds the name of the field the widget handles
        self.name = self.attrs.get('name', 'unnamed')
        self.record = None

        # Some widgets might want to change their color set.
        self.colors = {
            'invalid': '#FF6969',
            'readonly': '#e3e3e3',
            'required': '#ddddff',
            'normal': 'white'
        }

    def addShortcut(self, keys):
        if not keys:
            return
        shortcut = QShortcut(QKeySequence(keys), self)
        self.connect(shortcut, SIGNAL('activated()'), self.setFocus)

    def initialize(self):
        self.addShortcut(eval(self.attrs.get('use', '{}')).get('shortcut', ''))

    def showEvent(self, event):
        if not self._isInitialized:
            self._isInitialized = True
            self.initGui()
            self.initialize()
        if not self._isUpToDate:
            self._isUpToDate = True
            if self.record:
                self.showValue()
            self.updateColor()
        return QWidget.showEvent(self, event)

    def showHelp(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        helpWidget = Help.HelpWidget(self.sender())
        helpWidget.setLabel(self.attrs.get('string', ''))
        helpWidget.setHelp(self.attrs.get('help', ''))
        helpWidget.setType(helpWidget.FieldType)
        if self.record:
            # TODO: self.record should be optional
            helpWidget.setFilter((self.record.group.resource, self.name))
        helpWidget.show()
        QApplication.restoreOverrideCursor()

    # @brief This function is called the first time the widget is shown.
    #
    # It can be used by widgets to initialize GUI elements that are slow to
    # execute. The advantage of using this function is that if the user never
    # sees the widget (because it's in another tab, for example), it will never
    # be called, improving form loading time.
    #
    # It's ensured that this function is called before any call to showValue() or
    # storeValue() happens.
    def initGui(self):
        return

    # @brief Sets the default value to the field.
    #
    # Note that this requires a call to the server.
    def setToDefault(self):
        try:
            model = self.record.group.resource
            res = Rpc.session.call('/object', 'execute',
                                   model, 'default_get', [self.attrs['name']])
            self.record.setValue(self.name, res.get(self.name, False))
            self.display()
        except:
            QMessageBox.warning(None, _('Operation not permited'), _(
                'You can not set to the default value here !'))
            return False

    def inheritView(self):
        view_id = self.attrs.get('x-view')
        if not view_id:
            return
        view_id = re.findall('\d+', view_id)
        if not view_id:
            return
        view_id = int(view_id[0])
        view = Rpc.RpcProxy('ir.ui.view')
        records = view.read([view_id], ['name', 'model', 'xml_id'])
        record = records[0]

        id = record['xml_id'].split('.')[-1]

        arch = """
<openerp>
<data>
    <record model="ir.ui.view" id="%(id)s">
        <field name="name">%(name)s</field>
        <field name="model">%(model)s</field>
	<field name="type">form</field>
        <field name="inherit_id" ref="%(xml_id)s"/>
        <field name="arch" type="xml">
            <field name="%(field)s" position="after">
		<field name=""/>
            </field>
        </field>
    </record>
</data>
</openerp>""" % {
            'id': id,
            'name': record['name'],
            'model': record['model'],
            'xml_id': record['xml_id'],
            'field': self.attrs.get('name', ''),
        }
        fd, fileName = tempfile.mkstemp(suffix='.txt')
        os.write(fd, arch)
        os.close(fd)
        Common.openFile(fileName)

    # @brief Opens the FieldPreferencesDialog to set the current value as default for this field.
    def setAsDefault(self):
        if not self.view:
            return
        deps = []
        wid = self.view.widgets
        for wname, wview in self.view.widgets.items():
            if wview.attrs.get('change_default', False):
                value = wview.record.value(wview.name)
                deps.append((wname, wname, value, value))
        value = self.record.default(self.name)
        model = self.record.group.resource
        dialog = FieldPreferencesDialog(self.attrs['name'], self.attrs.get(
            'string', self.attrs['name']), model, value, deps)
        dialog.exec_()

    def updateColor(self):
        if self.record and not self.record.isFieldValid(self.name):
            self.setColor('invalid')
        elif self._readOnly:
            self.setColor('readonly')
        elif self._required:
            self.setColor('required')
        else:
            self.setColor('normal')

    # @brief This function is called when the widget has to be Read-Only.
    # When implementing a new widget, please use setEnabled( not ro ) instead
    # of read-only. The gray color gives information to the user so she knows
    # the field can't be modified
    def setReadOnly(self, ro):
        self._readOnly = ro
        self.updateColor()

    # @brief This function returns True if the field is read-only. False otherwise.
    def isReadOnly(self):
        return self._readOnly

    # @brief Updates the background color depending on widget state.
    #
    # Possible states are: invalid, readonly, required and normal.
    def refresh(self):
        self.setReadOnly(self._readOnly)

    # @brief Use it in your widget to return the widget in which you want the color
    # indicating the obligatory, normal, ... etc flags to be set.
    # By default colorWidget() returns self.
    def colorWidget(self):
        return self

    # @brief Use this function to return the menuEntries your widget wants to show
    # just before the context menu is shown. Return a list of tuples in the form:
    # [ (_('Menu text'), function/slot to connect the entry, True (for enabled) or False (for disabled) )]
    def menuEntries(self):
        return []

    # @brief Sets the background color to the widget returned by colorWidget().
    # name should contain the current state ('invalid', 'readonly', 'required' or 'normal')
    #
    # The appropiate color for each state is stored in self.colors dictionary.
    def setColor(self, name):
        color = QColor(self.colors.get(name, 'white'))
        palette = QPalette()
        palette.setColor(QPalette.Active, QPalette.Base, color)
        self.colorWidget().setPalette(palette)

    # @brief Installs the eventFilter on the given widget so the popup
    # menu will be shown on ContextMenu event. Also data on the widget will
    # be stored in the record when the widget receives the FocusOut event.
    def installPopupMenu(self, widget):
        widget.installEventFilter(self)

    # @brief Reimplements eventFilter to show the context menu and store
    # information when the widget loses the focus. This function will be
    # used on the widget you give to installPopupMenu.
    def eventFilter(self, target, event):
        if event.type() == QEvent.ContextMenu:
            self.showPopupMenu(target, event.globalPos())
            return True
        if event.type() == QEvent.FocusOut:
            if self.record:
                self.store()
        return False

    # @brief Shows a popup menu with default and widget specific
    # entries.
    def showPopupMenu(self, parent, position):
        entries = self.defaultMenuEntries[:]
        new = self.menuEntries()

        if len(new) > 0:
            entries = entries + [(None, None, None)] + new

        if Settings.value('koo.developer_mode', False):
            entries.append((None, None, None))
            entries.append((_('Inherit View'), self.inheritView, 1))

        if not entries:
            return

        try:
            menu = parent.createStandardContextMenu()
            menu.setParent(parent)
            menu.addSeparator()
        except:
            menu = QMenu(parent)
        for title, slot, enabled in entries:
            if title:
                item = QAction(title, menu)
                if slot:
                    self.connect(item, SIGNAL("triggered()"), slot)
                item.setEnabled(enabled)
                menu.addAction(item)
            else:
                menu.addSeparator()
        menu.popup(position)

    # @brief Call this function/slot when your widget changes the
    # value. This is needed for the onchange option in the
    # server modules. Usually you'll call it on lostFocus if
    # there's a TextBox or on selection, etc.
    def modified(self):
        if not self.record:
            return
        self.store()

    # @brief Override this function. This will be called by display()
    # when it wants the value to be shown in the widget
    def showValue(self):
        pass

    # @brief Override this function. It will be used whenever there
    # is no model or have created a new record.
    def clear(self):
        pass

    # @brief This function displays the current value of the field in the record
    # in the widget.
    #
    # Do not reimplement this function, override clear() and showValue() instead
    def display(self):
        if not self.record:
            self._readOnly = True
            self.clear()
            self.refresh()
            return
        self._readOnly = self.record.isFieldReadOnly(self.name)
        self._required = self.record.isFieldRequired(self.name)
        self.refresh()
        if self.isVisible():
            if not self._isInitialized:
                self._isInitialized = True
                self.initGui()
                self.initialize()
            self._isUpToDate = True
            self.showValue()
        else:
            self._isUpToDate = False

    def reset(self):
        self.refresh()

    # @brief Sets the current record for the widget.
    def load(self, record):
        self.record = record
        self.display()

    # @brief Stores information in the widget to the record.
    # Reimplement this function in your widget.
    def storeValue(self):
        pass

    # @brief Stores information in the widget to the record.
    # This is the function you should call when you want the field
    # to store information back into the model. This function may
    # NOT store information if it has not changed.
    def store(self):
        if not self._isUpToDate:
            return
        self.storeValue()

    def saveState(self):
        return QByteArray()

    def restoreState(self, state):
        pass

# vim:noexpandtab:smartindent:tabstop=8:softtabstop=8:shiftwidth=8:
