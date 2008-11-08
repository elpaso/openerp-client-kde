##############################################################################
#
# Copyright (c) 2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
from Koo.KooChart import *

import datetime 
import time
import locale

DT_FORMAT = '%Y-%m-%d'
DHM_FORMAT = '%Y-%m-%d %H:%M:%S'
HM_FORMAT = '%H:%M:%S'

if not hasattr(locale, 'nl_langinfo'):
	locale.nl_langinfo = lambda *a: '%x'

if not hasattr(locale, 'D_FMT'):
	locale.D_FMT = None


class ChartGraphicsView( QGraphicsView ):
	def __init__(self, parent=None):
		QGraphicsView.__init__(self, parent)
		self.setRenderHints( QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform )
		self.scene = QGraphicsScene(self)
		self.setScene( self.scene )
		self.chart = None

	def setModel(self, model):
		self._model = model

	def setFields(self, fields):
		self._fields = fields

	def setType(self, type):
		self._type = type

	def setAxis(self, axis):
		self._axis = axis

	def setGroups(self, groups):
		self._groups = groups

	def setAxisData(self, axisData):
		self._axisData = axisData

	def setAxisGroupField(self, axisGroupField):
		self._axisGroupField = axisGroupField

	def setOrientation(self, orientation):
		self._orientation = orientation

	def resizeEvent(self, event):
		if self.chart:
			self.chart.setSize( QSize( self.size().width() - 100, self.size().height() - 100 ) )

	def display(self, models):
		self._models = models
		if not self.chart:
			if self._type == 'pie': 
				self.chart = GraphicsPieChartItem()
			else:
				self.chart = GraphicsBarChartItem()
			self.chart.setSize( self.size() )
			self.scene.addItem( self.chart )

		# Put all values to be shown in the datas list
		datas = []
		for m in models:
			res = {}
			for x in self._axisData.keys():
				if self._fields[x]['type'] in ('many2one', 'char','time','text','selection'):
					res[x] = m.value(x) 
				elif self._fields[x]['type'] == 'date':
					date = time.strptime(m.value(x), DT_FORMAT)
					res[x] = time.strftime(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y'), date)
				elif self._fields[x]['type'] == 'datetime':
					date = time.strptime(m.value(x), DHM_FORMAT)
					if 'tz' in Rpc.session.context:
						try:
							import pytz
							lzone = pytz.timezone(Rpc.session.context['tz'])
							szone = pytz.timezone(Rpc.session.timezone)
							dt = datetime.datetime(date[0], date[1], date[2], date[3], date[4], date[5], date[6])
							sdt = szone.localize(dt, is_dst=True)
							ldt = sdt.astimezone(lzone)
							date = ldt.timetuple()
						except:
							pass
					res[x] = time.strftime(locale.nl_langinfo(locale.D_FMT).replace('%y', '%Y')+' %H:%M:%S', date)
				else:
					res[x] = float(m.value(x))
			datas.append(res)

		# Calculate the rest of values
		operators = {
			'+': lambda x,y: x+y,
			'*': lambda x,y: x*y,
			'min': lambda x,y: min(x,y),
			'max': lambda x,y: max(x,y),
			'**': lambda x,y: x**y
		}
		axis_group = {}
		keys = {}
		data_axis = []
		if self._groups:
			for field in self._axis[1:]:
				data = {}
				for d in datas:
					group_eval = ','.join( [d[x] for x in self._groups] )
					axis_group[group_eval] = 1

					data.setdefault( d[self._axis[0]], {} )

					if group_eval in  data[d[self._axis[0]]]:
						oper = operators[self._axisData[field].get('operator', '+')]
						data[d[self._axis[0]]][group_eval] = oper(data[d[self._axis[0]]][group_eval], d[field])
					else:
						data[d[self._axis[0]]][group_eval] = d[field]
				data_axis.append(data)
			axis_group = axis_group.keys()
			axis_group.sort()

		fields = set()
		for field in self._axis[1:]:
			fields.add( self._fields[field]['name'] )
		fields = list(fields)
		fields.sort()

		labels = [self._fields[x]['string'] for x in self._axis[1:]]

		categories = set()
		for x in datas:
			categories.add( x[ self._axis[0] ] or '' )
		categories = list(categories)
		categories.sort()
		
		if self._type == 'pie': 
			values = []
			for x in datas:
				values.append( x[self._axis[1]] )

			self.chart.setValues( values ) 
			self.chart.setLabels( categories )
		else:
			values = []
			for x in categories:
				for y in datas:
					if y[self._axis[0]] == x:
						break
				value = []
				for f in fields:
					value.append( y[f] )
				values.append( value )

			self.chart.setValues( values )
			self.chart.setLabels( labels )
			self.chart.setCategories( categories )
