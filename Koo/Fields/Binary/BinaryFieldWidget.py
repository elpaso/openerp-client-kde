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

import os
import tempfile

from Koo.Fields.AbstractFieldWidget import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.uic import *

from Koo.Common import Common

(BinaryFieldWidgetUi, BinaryFieldWidgetBase) = loadUiType( Common.uiPath('binary.ui') ) 

class BinaryFieldWidget(AbstractFieldWidget, BinaryFieldWidgetUi):
	def __init__(self, parent, model, attrs={}):
		AbstractFieldWidget.__init__(self, parent, model, attrs)
		BinaryFieldWidgetUi.__init__(self)
		self.setupUi(self)

		self.connect( self.pushNew, SIGNAL('clicked()'), self.slotNew )
		self.connect( self.pushRemove, SIGNAL('clicked()'),self.slotRemove )
		self.connect( self.pushSave, SIGNAL('clicked()'),self.slotSave )

		self.installPopupMenu( self.uiBinary )
		
	def setReadOnly(self, value):
		self.uiBinary.setEnabled( not value )
		self.pushNew.setEnabled( not value )
		self.pushRemove.setEnabled( not value )

	def menuEntries(self):
		pix = QPixmap()
		if self.model.value(self.name):
			enableApplication = True
		else:
			enableApplication = False

		if pix.loadFromData( self.model.value(self.name) ):
			enableImage = True
		else:
			enableImage = False
		return [ (_('Open...'), self.openApplication, enableApplication), 
			 (_('Show &image...'), self.showImage, enableImage) ]

	def openApplication(self):
		if not self.model.value(self.name):
			return

		# Under windows platforms we need to create the temporary
		# file with an appropiate extension, otherwise the system
		# won't be able to know how to open it. The only way we have
		# to know what kind of file it is, is if the fname_widget property
		# was set, and pick up the extension from that field.
		extension = ''
		if 'fname_widget' in self.attrs:
			fileName = self.model.value( self.attrs['fname_widget'] )
			if fileName:
				extension = '.%s' % fileName.rpartition('.')[2]

		fileName = tempfile.mktemp( extension )
		fp = file(fileName,'wb+')
		fp.write( self.model.value(self.name) )
		fp.close()
		Common.openFile( fileName )

	def showImage(self):
		if not self.model.value(self.name): 
			return
		dialog = QDialog( self )
		label = QLabel( dialog )
		pix = QPixmap()
		pix.loadFromData( self.model.value(self.name) )
		label.setPixmap( pix )
		layout = QHBoxLayout( dialog )
		layout.addWidget( label )
		dialog.exec_()

	def slotNew(self):
		try:
			filename = QFileDialog.getOpenFileName(self, _('Select the file to attach'))
			if filename.isNull():
				return
			filename = unicode(filename)
			value = file(filename, 'rb').read()
			self.model.setValue( self.name, value )
			self.uiBinary.setText( _('%d bytes') % len(value) )

			# The binary widget might have a 'fname_widget' attribute
			# that stores the file name in the field indicated by 'fname_widget'
			if 'fname_widget' in self.attrs:
				w = self.attrs['fname_widget']
				self.model.setValue( w, os.path.basename(filename) )
				if self.view:
					self.view.widgets[w].load(self.model)
		except:
			QMessageBox.information(self, '', _('Error reading the file'))

	def slotSave(self):
		try:
			filename = QFileDialog.getSaveFileName( self, _('Save as...') )
			if filename:
				fp = file(filename,'wb+')
				fp.write( self.model.value(self.name) )
				fp.close()
		except:
			QMessageBox.information(self, '', _('Error writing the file!'))

	def slotRemove(self):
		self.model.setValue( self.name, False )
		self.clear()
		self.modified()
		if 'fname_widget' in self.attrs:
			w = self.attrs['fname_widget']
			self.model.setValue( w, False )
			if self.view:
				self.view.widgets[w].load(self.model)

	def showValue(self):
		if self.model.value( self.name ):
			size = len( self.model.value( self.name ) )
			self.uiBinary.setText( _('%d bytes') % size ) 
		else:
			self.clear()

	def clear(self):
		self.uiBinary.clear()

	# This widget is a bit special. We don't set the value
	# here. We do it in the slotNew, so we don't have two copies
	# of the file (which can be pretty big) in memory.
	def store(self):
		pass

	def colorWidget(self):
		return self.uiBinary

