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

## In this module you can find various functions that help calendar 
# widgets (date, time & datetime) in widget.view.form, widget.view.tree and 
# Search modules. Probably others will use them in the future. These 
# functions provide very simple ways of parsing user input, and here we define 
# the standard output format too. Also from and to Storage functions are 
# provided that ensure date and time are formated the way the storage system 
# expects.
#
# Also a calendar popup is provided for use in widgets.
#
from PyQt4.QtCore import *
from PyQt4.QtGui import * 
from PyQt4.uic import *
import math
import common

## @brief Converts a QDate object into a Python string
def dateToText( date ):
	return str( date.toString( 'dd/MM/yyyy' ) )

## @brief Converts a QTime object into a Python string
def timeToText( time ):
	return str( time.toString( 'hh:mm:ss' ) )

## @brief Converts a QDateTime object into a Python string
def dateTimeToText( dateTime ):
	return str( dateTime.toString( 'dd/MM/yyyy hh:mm:ss' ) )

## @brief Converts a float (type floatTime) into a Python string
def floatTimeToText( value ):
	t = '%02d:%02d' % (math.floor(abs(value)),round(abs(value)%1+0.01,2) * 60)
	if value<0:
		t = '-'+t
	return t

## @brief Converts a QDate object into a Python string ready to be sent to the 
# server.
def dateToStorage( date ):
	return str( date.toString( 'yyyy-MM-dd' ) )

## @brief Converts a QTime object into a Python string ready to be sent to the 
# server.
def timeToStorage( time ):
	return str( time.toString( 'hh:mm:ss' ) )
	
## @brief Converts a QDateTime object into a Python string ready to be sent to 
# the server.
def dateTimeToStorage( dateTime ):
	return str( dateTime.toString( 'yyyy-MM-dd hh:mm:ss' ) )

## @brief Converts a Python string or QString into a QDate object
def textToDate( text ):
	inputFormats = ["dd/MM/yyyy", "dd-MM-yyyy", 'dd-MM-yy', 'dd/MM/yy', 'dd-M-yy', 'd-M-yy', 'd-MM-yy']
	for x in inputFormats:
		date  = QDate.fromString( text, x )
		if date.isValid():
			break
	return date

## @brief Converts a Python string or QString into a QTime object
def textToTime( text ):
	inputFormats = ['h:m:s', 'h:m', 'hh:mm:ss', 'h.m.s', 'h.m']
	for x in inputFormats:
		time = QTime.fromString( text, x )
		if time.isValid():
			break
	return time

## @brief Converts a Python string or QString into a QDateTime object
def textToDateTime( text ):
	inputFormats = ['dd/MM/yyyy h:m:s', "dd/MM/yyyy", "dd-MM-yyyy", 'dd-MM-yy', 'dd/MM/yy', 'dd-M-yy', 'd-M-yy', 'd-MM-yy' ]
	for x in inputFormats:
		datetime = QDateTime.fromString( text, x )
		if datetime.isValid():
			break
	return datetime

## @brief Converts a Python string into a float (floatTime) 
def textToFloatTime( text ):
	try:
		if text and ':' in text:
			return round(int(text.split(':')[0]) + int(text.split(':')[1]) / 60.0,2)
		else:
			return locale.atof(text)
	except:
		return 0.0

## @brief Converts a Python string comming from the server into a QDate object
def storageToDate( text ):
	return QDate.fromString( text, 'yyyy-MM-dd' )

## @brief Converts a Python string comming from the server into a QTime object
def storageToTime( text ):
	return QTime.fromString( text, 'h:m:s' )

## @brief Converts a Python string comming from the server into a QDateTime object
def storageToDateTime( text ):
	return QDateTime.fromString( text, 'yyyy-MM-dd h:m:s' )



## @brief The PopupCalendar class, provides a simple way to show a calendar 
# where the user can pick up a date. 
#
# You simply need to call PopupCalendar(widget) where widget
# should be a QLineEdit or similar. The Popup will fill in the widget itself.
#
# If you want the user to be able to select date and time, specify showTime=True
# when constructing the object.
#
# You may force the pop-up to store and close with the storeOnParent() function.
#
# Of course, PopupCalendar uses the other ToTime and ToText helper functions.
#
class PopupCalendar(QWidget):
	def __init__(self, parent, showTime = False):
		QWidget.__init__(self, parent)
		loadUi( common.uiPath('datetime.ui'), self )
		self.showTime = showTime
		if self.showTime:
			self.uiTime.setText( textToDateTime( str(parent.text()) ).time().toString() )
			self.connect( self.uiTime, SIGNAL('returnPressed()'), self.storeOnParent )
		else:
			self.uiTime.hide()
			self.labelTime.hide()

		self.setWindowFlags( Qt.Popup )
		self.setWindowModality( Qt.ApplicationModal )
		pos = parent.mapToGlobal( parent.pos() )
		self.move( pos.x(), pos.y() + parent.height() )
		self.connect( self.uiCalendar, SIGNAL('activated(QDate)'), self.storeOnParent )
		if self.showTime:
			self.uiCalendar.setSelectedDate( textToDateTime( parent.text() ).date() )
		else:
			self.uiCalendar.setSelectedDate( textToDate( parent.text() ) )
		self.uiCalendar.setFirstDayOfWeek( Qt.Monday )
		self.show()
		if self.showTime:
			self.uiTime.setFocus()
		else:
			self.uiCalendar.setFocus()

	def storeOnParent(self):
		date = self.uiCalendar.selectedDate()
		text = dateToText( date )
		if self.showTime: 
			time = textToTime( self.uiTime.text() )
			if time.isValid():
				text = text + ' ' + timeToText(time)
			else:
				text = text + ' ' + '00:00:00'
		self.parent().setText( text )
		self.emit(SIGNAL('selected()'))
		self.close()
