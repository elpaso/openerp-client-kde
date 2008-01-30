##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: url.py 3861 2006-08-22 09:14:03Z pinky $
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

from common import common
from abstractformwidget import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.uic import *

class UrlFormWidget(AbstractFormWidget):
	def __init__(self, parent, model, attrs={}):
		AbstractFormWidget.__init__(self, parent, model, attrs)
		loadUi( common.uiPath('url.ui'), self )

		
		self.uiUrl.setMaxLength( int( attrs.get('size',16)))
		if attrs.get('invisible',False):
			self.uiUrl.hide()
		else:
			self.uiUrl.show()
		self.connect( self.pushOpenUrl, SIGNAL('clicked()'), self.openUrl )
		self.uiUrl.installEventFilter( self )

	def eventFilter( self, target, event ):
		return self.showPopupMenu( target, event )

	def store(self):
		return self.model.setValue(self.name, str( self.uiUrl.text() ) or False)

	def clear( self ):
		self.uiUrl.setText('')

	def showValue(self):
		self.uiUrl.setText(self.model.value(self.name) or '')

	def setReadOnly(self, value):
		self.uiUrl.setEnabled( not value )

	def openUrl(self):
		value =  str(self.uiUrl.text()).strip()
		if value != '':
			QDesktopServices.openUrl( QUrl(value) )

class EMailFormWidget(UrlFormWidget):
	def openUrl(self):
		value =  str(self.uiUrl.text()).strip()
		if value != '':
			QDesktopServices.openUrl( QUrl('mailto:' + value) )

class CallToFormWidget(UrlFormWidget):
	def openUrl(self):
		value = str(self.uiUrl.text()).strip()
		if value != '':
			QDesktopServices.openUrl( QUrl('callto:%s' + value) )

class SipFormWidget(UrlFormWidget):
	def openUrl(self):
		value = str(self.uiUrl.text()).strip()
		if value != '':
			QDesktopServices.openUrl( QUrl('sip:%s' + value) )

# vim:noexpandtab:
