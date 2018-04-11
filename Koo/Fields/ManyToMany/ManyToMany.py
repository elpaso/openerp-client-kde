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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from Koo.Common.Ui import *

from Koo.Common import Api
from Koo.Common import Common
from Koo.Common import Shortcuts
from Koo import Rpc

from Koo.Screen.Screen import Screen
from Koo.Model.Group import RecordGroup
from Koo.Fields.AbstractFieldWidget import *
from Koo.Fields.AbstractFieldDelegate import *
from Koo.Dialogs.SearchDialog import SearchDialog

(ManyToManyFieldWidgetUi, ManyToManyFieldWidgetBase) = loadUiType(
    Common.uiPath('many2many.ui'))


class ManyToManyFieldWidget(AbstractFieldWidget, ManyToManyFieldWidgetUi):
    def __init__(self, parent, model, attrs={}):
        AbstractFieldWidget.__init__(self, parent, model, attrs)
        ManyToManyFieldWidgetUi.__init__(self)
        self.setupUi(self)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.connect(self.pushAdd, SIGNAL("clicked()"), self.slotAdd)
        self.connect(self.pushRemove, SIGNAL("clicked()"), self.remove)
        self.connect(self.uiText, SIGNAL('editingFinished()'), self.match)

        self.scSearch = QShortcut(self.uiText)
        self.scSearch.setKey(Shortcuts.SearchInField)
        self.scSearch.setContext(Qt.WidgetShortcut)
        self.connect(self.scSearch, SIGNAL('activated()'), self.add)

        self.scClear = QShortcut(self.screen)
        self.scClear.setKey(Shortcuts.ClearInField)
        self.scClear.setContext(Qt.WidgetWithChildrenShortcut)
        self.connect(self.scClear, SIGNAL('activated()'), self.remove)

        self.connect(self.screen, SIGNAL('activated()'), self.open)

        self.connect(self.pushBack, SIGNAL("clicked()"), self.previous)
        self.connect(self.pushForward, SIGNAL("clicked()"), self.next)
        self.connect(self.screen, SIGNAL(
            'recordMessage(int,int,int)'), self.setLabel)

        self.installPopupMenu(self.uiText)
        self.old = None
        self.latestMatch = None
        self.searching = False

    def initGui(self):
        if self.record:
            group = self.record.value(self.name)
        else:
            group = None
        if not group:
            group = RecordGroup(self.attrs['relation'])
            group.setDomainForEmptyGroup()
        self.screen.setRecordGroup(group)
        self.screen.setViewTypes(['tree'])
        self.screen.setEmbedded(True)

    def next(self):
        self.screen.displayNext()

    def previous(self):
        self.screen.displayPrevious()

    def setLabel(self, position, count, value):
        name = '_'
        if position >= 0:
            name = str(position + 1)
        line = '(%s/%s)' % (name, count)
        self.uiLabel.setText(line)

    def open(self):
        if not (QApplication.keyboardModifiers() & Qt.ControlModifier):
            return

        if not self.screen.currentRecord():
            return
        id = self.screen.currentRecord().id
        if not id:
            return

        if QApplication.keyboardModifiers() & Qt.ShiftModifier:
            target = 'background'
        else:
            target = 'current'
        Api.instance.createWindow(False, self.attrs['relation'], id, [
                                  ('id', '=', id)], 'form', mode='form,tree', target=target)

    def match(self):
        if self.searching:
            return
        if not self.record:
            return
        text = unicode(self.uiText.text()).strip()
        if text == '':
            self.uiText.clear()
            return
        # As opening the search dialog will emit the editingFinished signal,
        # we need to know we're searching by setting self.searching = True
        self.searching = True
        self.add()
        self.searching = False

    def slotAdd(self):
        text = unicode(self.uiText.text()).strip()
        # As opening the search dialog will emit the editingFinished signal,
        # we need to know we're searching by setting self.searching = True
        self.searching = True
        self.add()
        self.searching = False

    def add(self):
        # As the 'add' button modifies the model we need to be sure all other fields/widgets
        # have been stored in the model. Otherwise the recordChanged() triggered
        # could make us lose changes.
        self.view.store()

        domain = self.record.domain(self.name)
        context = self.record.fieldContext(self.name)

        ids = Rpc.session.execute('/object', 'execute', self.attrs['relation'], 'name_search', unicode(
            self.uiText.text()), domain, 'ilike', context, False)
        ids = [x[0] for x in ids]
        if unicode(self.uiText.text()) == '' or len(ids) != 1:
            dialog = SearchDialog(
                self.attrs['relation'], sel_multi=True, ids=ids, domain=domain, context=context)
            if dialog.exec_() == QDialog.Rejected:
                self.uiText.clear()
                return
            ids = dialog.result

        self.screen.load(ids)
        self.screen.display()
        self.uiText.clear()
        # Manually set the current model and field as modified
        # This is not necessary in case of removing an item.
        # Maybe a better option should be found. But this one works just right.
        self.screen.group.recordChanged(None)
        self.screen.group.recordModified(None)

    def remove(self):
        # As the 'remove' button modifies the model we need to be sure all other fields/widgets
        # have been stored in the model. Otherwise the recordChanged() triggered
        # could make us lose changes.
        self.view.store()
        self.screen.remove()
        self.screen.display()

    def setReadOnly(self, value):
        AbstractFieldWidget.setReadOnly(self, value)
        self.uiText.setEnabled(not value)
        self.pushAdd.setEnabled(not value)
        self.pushRemove.setEnabled(not value)

    def clear(self):
        self.uiText.setText('')
        self.screen.setRecordGroup(None)
        self.screen.display()

    def showValue(self):
        group = self.record.value(self.name)
        self.screen.setRecordGroup(group)
        self.screen.display()

    # We do not store anything here as elements are added and removed in the
    # Screen (self.screen). The only thing we need to take care of (as noted
    # above) is to ensure that the model and field are marked as modified.
    def storeValue(self):
        pass

    def saveState(self):
        self.screen.storeViewSettings()
        return AbstractFieldWidget.saveState(self)


class ManyToManyFieldDelegate(AbstractFieldDelegate):
    def setModelData(self, editor, kooModel, index):
        if unicode(editor.text()) == unicode(index.data(Qt.DisplayRole).toString()):
            return
        # We expecte a KooModel here
        model = kooModel.recordFromIndex(index)

        #model.setData( index, QVariant( editor.currentText() ), Qt.EditRole )
        domain = model.domain(self.name)
        context = model.fieldContext(self.name)

        ids = Rpc.session.execute('/object', 'execute', self.attributes['relation'], 'name_search', unicode(
            editor.text()), domain, 'ilike', context, False)
        ids = [x[0] for x in ids]
        if len(ids) != 1:
            dialog = SearchDialog(
                self.attributes['relation'], sel_multi=True, ids=ids, domain=domain, context=context)
            if dialog.exec_() == QDialog.Rejected:
                return
            ids = dialog.result

        ids = [QVariant(x) for x in ids]
        kooModel.setData(index, QVariant(ids), Qt.EditRole)
