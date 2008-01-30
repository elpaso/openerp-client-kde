##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: binary.py 4752 2006-12-01 15:11:37Z ced $
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

import base64
import os
import tempfile

from abstractformwidget import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.uic import *

from common import common

class BinaryFormWidget(AbstractFormWidget):
	def __init__(self, parent, model, attrs={}):
		AbstractFormWidget.__init__(self, parent, model, attrs)

		loadUi( common.uiPath('binary.ui'), self )
		self.connect( self.pushNew, SIGNAL('clicked()'), self.slotNew )
		self.connect( self.pushRemove, SIGNAL('clicked()'),self.slotRemove )
		self.connect( self.pushSave, SIGNAL('clicked()'),self.slotSave )

		self.value = False
		self.uiBinary.installEventFilter( self )
		
	def setReadOnly(self, value):
		self.uiBinary.setEnabled( not value )
		self.pushNew.setEnabled( not value )
		self.pushRemove.setEnabled( not value )
		self.pushSave.setEnabled( not value )

	def menuEntries(self):
		pix = QPixmap()
		if self.value:
			enableApplication = True
		else:
			enableApplication = False

		if pix.loadFromData( base64.decodestring(self.value) ):
			enableImage = True
		else:
			enableImage = False
		return [ (_('Open...'), self.openApplication, enableApplication), 
			 (_('Show &image...'), self.showImage, enableImage) ]

	def openApplication(self):
		if not self.value:
			return
		fileName = tempfile.mktemp()
		fp = file(fileName,'wb+')
		fp.write(base64.decodestring(self.value))
		fp.close()
		if os.name == 'nt':
			os.startfile(fileName)
		else:
			os.spawnlp(os.P_NOWAIT, 'kfmclient', 'kfmclient', 'exec', fileName )

	def showImage(self):
		if not self.value: 
			return
		dialog = QDialog( self )
		label = QLabel( dialog )
		pix = QPixmap()
		pix.loadFromData( base64.decodestring(self.value) )
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
			self.value = file(filename).read()
			self.uiBinary.setText( _('%d bytes') % len(self.value) )
			self.value = base64.encodestring(file(filename).read())

			# The binary widget might have a 'fname_widget' attribute
			# that stores the file name in the field indicated by 'fname_widget'
			if 'fname_widget' in self.attrs:
				w = self.attrs['fname_widget']
				self.model.setValue( w, os.path.basename(filename) )
				self.view.widgets[w].load(self.model)
		except:
			QMessageBox.information(self, '', _('Error reading the file'))

	def slotSave(self):
		try:
			filename = QFileDialog.getSaveFileName( self, _('Save attachment as...') )
			if filename:
				fp = file(filename,'wb+')
				fp.write(base64.decodestring(self.value))
				fp.close()
		except:
			QMessageBox.information(self, '', _('Error writing the file!'))

	def slotRemove(self):
		self.value = False
		self.clear()
		if 'fname_widget' in self.attrs:
			w = self.attrs['fname_widget']
			self.model.setValue( w, False )
			self.view.widgets[w].load(self.model)

	def showValue(self):
		self.value = self.model.value( self.name )
		if self.value:
			size = len(base64.decodestring(self.value))
			self.uiBinary.setText( _('%d bytes') % size ) 
		else:
			self.clear()

	def clear(self):
		self.uiBinary.setText('')

	# This widget is a bit special. We don't set the value
	# here. We do it in the slotNew, so we don't have two copies
	# of the file (which can be pretty big) in memory.
	def store(self):
		print "Model:", self.model
		print " Name:", self.name, "Value:", self.value
		self.model.setValue( self.name, self.value )
		return

	def colorWidget(self):
		return self.uiBinary
