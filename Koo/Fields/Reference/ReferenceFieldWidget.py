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
from PyQt4.uic import *

from Koo.Common import Common
from Koo.Common import Api
from Koo.Common import Shortcuts
from Koo.Dialogs.SearchDialog import SearchDialog

from Koo.Fields.AbstractFieldWidget import *
from Koo.Fields.ManyToOne import ScreenDialog

from Koo import Rpc
from Koo.Rpc import RpcProxy

(ReferenceFieldWidgetUi, ReferenceFieldWidgetBase ) = loadUiType( Common.uiPath('reference.ui') ) 

# This widget requires some ugly hacks. Mainly clearing the text fields once it's been
# modified and searched afterwards. This is due to the fact that the 'name' the server
# returns, if searched, might not be found again :(
class ReferenceFieldWidget(AbstractFieldWidget, ReferenceFieldWidgetUi):
	def __init__(self, parent, model, attrs={}):
		AbstractFieldWidget.__init__(self, parent, model, attrs)
		ReferenceFieldWidgetUi.__init__(self)
		self.setupUi(self)

		self.connect( self.pushNew, SIGNAL('clicked()'), self.new )
		self.connect( self.pushOpen, SIGNAL('clicked()'), self.open )
		self.connect( self.pushClear, SIGNAL('clicked()'), self.clear )
		self.setPopdown( attrs.get('selection',[]) )
		self.connect( self.uiModel, SIGNAL('currentIndexChanged(int)'), self.modelChanged )
		self.connect( self.uiText, SIGNAL( "editingFinished()" ), self.match )
		self.scNew = QShortcut( self.uiText )
		self.scNew.setContext( Qt.WidgetShortcut )
		self.scNew.setKey( Shortcuts.CreateInField )
		self.connect( self.scNew, SIGNAL('activated()'), self.new )

		self.scSearch  = QShortcut( self.uiText )
		self.scSearch.setContext( Qt.WidgetShortcut )
		self.scSearch.setKey( Shortcuts.SearchInField )
		self.connect( self.scSearch, SIGNAL('activated()'), self.open )

		self.uiModel.setEditable( False )
		self.installPopupMenu( self.uiText )

	def modelChanged(self, idx):
		if idx < 0:
			enabled = False
			self.uiText.clear()
		else:
			enabled = True
		self.uiText.setEnabled( enabled )
		self.pushOpen.setEnabled( enabled )
		self.pushNew.setEnabled( enabled )
		self.pushClear.setEnabled( enabled )

	def clear(self):
		# As the 'clear' button might modify the model we need to be sure all other fields/widgets
		# have been stored in the model. Otherwise the recordChanged() triggered by modifying
		# the parent model could make us lose changes.
		self.view.store()

		# This automatically refreshes the widget and thus clears
		# the uiModel combo and the uiText line edit
		if self.model:
			self.model.setValue(self.name, False)

	def setPopdown(self, selection):
		self.invertedModels = {}

		for (i,j) in selection:
			self.uiModel.addItem( j, QVariant(i) )
			self.invertedModels[i] = j

	def setReadOnly(self, value):
		self.uiModel.setEnabled( not value )
		if self.uiModel.currentIndex() < 0:
			value = True
		self.uiText.setEnabled( not value )
		self.pushNew.setEnabled( not value )
		self.pushOpen.setEnabled( not value )
		self.pushClear.setEnabled( not value )

	def colorWidget(self):
		return self.uiText

	def store(self):
		# No update of the model, the model is updated in real time 
		pass

	def search(self):
		domain = self.model.domain(self.name)
		context = self.model.fieldContext(self.name)
		resource = unicode(self.uiModel.itemData(self.uiModel.currentIndex()).toString())
		ids = Rpc.session.execute('/object', 'execute', resource, 'name_search', unicode(self.uiText.text()), domain, 'ilike', context)
		
		if len(ids)==1:
			id, name = ids[0]
			self.model.setValue(self.name, (resource, (id, name)) ) 
			self.display()
			return

		dialog = SearchDialog(resource, sel_multi=False, ids=[x[0] for x in ids], context=context, domain=domain)
		if dialog.exec_() == QDialog.Accepted and dialog.result:
			id = dialog.result[0]
			id, name = Rpc.session.execute('/object', 'execute', resource, 'name_get', [id], Rpc.session.context)[0]
			self.model.setValue(self.name, (resource, (id, name)) )
			self.display()

	def match(self):
		name = unicode(self.uiText.text())
		if name.strip() == '':
			self.model.setValue(self.name, False)
			return

		value = self.model.value(self.name)
		if value and value[1][1] == name:
			return
		self.search()

	def new(self):
		resource = unicode(self.uiModel.itemData(self.uiModel.currentIndex()).toString())
		dialog = ScreenDialog( self )
		dialog.setup( resource )
		dialog.setAttributes( self.attrs )
		if dialog.exec_() == QDialog.Accepted:
			resource = unicode(self.uiModel.itemData(self.uiModel.currentIndex()).toString())
			self.model.setValue(self.name, (resource, dialog.model) )

	def open(self):
		# As the 'open' button might modify the model we need to be sure all other fields/widgets
		# have been stored in the model. Otherwise the recordChanged() triggered by modifying
		# the parent model could make us lose changes.
		self.view.store()

		value = self.model.value(self.name)
		if value:
			model, (id, name) = value
			# If Control Key is pressed when the open button is clicked
			# the record will be opened in a new tab. Otherwise it's opened
			# in a new modal dialog.
			if QApplication.keyboardModifiers() & Qt.ControlModifier:
				Api.instance.createWindow(False, model, id, [], 'form', mode='form,tree')
			else:	
				dialog = ScreenDialog( self )
				dialog.setup( model, id )
				dialog.setAttributes( self.attrs )
				dialog.exec_()
		else:
			self.search()

	def clear(self):
		self.uiModel.setCurrentIndex(-1)
		if self.model:
			self.model.setValue( self.name, False )
			self.display()
		
	def showValue(self):
		value = self.model.value(self.name) 
		if value:
			model, (id, name) = value
			self.uiModel.setCurrentIndex( self.uiModel.findText(self.invertedModels[model]) )
			if not name:
				id, name = RpcProxy(model).name_get([id], Rpc.session.context)[0]
			self.uiText.setText(name)
			self.pushOpen.setIcon( QIcon(":/images/images/folder.png") )
		else:
			self.uiText.clear()
			self.uiModel.setCurrentIndex(-1)
			self.pushOpen.setIcon( QIcon(":/images/images/find.png") )
