##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: one2many_list.py 4773 2006-12-05 11:01:20Z ced $
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


import gettext
from common import common


from widget.screen import Screen

import rpc
import time
from modules.gui.window.win_search import win_search
import service
from abstractformwidget import *

class action(AbstractFormWidget):
	def __init__(self,  parent, model, attrs={}):
		AbstractFormWidget.__init__( self, parent, model, attrs )

		self.colors['normal'] = self.palette().color( self.backgroundRole() )	
		self.act_id=attrs['name']
		res = rpc.session.execute('/object', 'execute', 'ir.actions.actions', 'read', [self.act_id], ['type'], rpc.session.context)
		if not res:
			raise Exception, 'ActionNotFound'
		type=res[0]['type']

		
		self.action = rpc.session.execute('/object', 'execute', type, 'read', [self.act_id], False, rpc.session.context)[0]
		if 'view_mode' in attrs:
			self.action['view_mode'] = attrs['view_mode']

		if self.action['type']=='ir.actions.act_window':
			if not self.action.get('domain', False):
				self.action['domain']='[]'
			self.context = {'active_id': False, 'active_ids': []}
			self.context.update(eval(self.action.get('context', '{}'), self.context.copy()))
			a = self.context.copy()
			a['time'] = time
			#self.domain = common.expr_eval(self.action['domain'], a)
			self.domain = rpc.session.evaluateExpression(self.action['domain'], a)

			view_id = []
			if self.action['view_id']:
				view_id = [self.action['view_id'][0]]
			if self.action['view_type']=='form':
				mode = (self.action['view_mode'] or 'form,tree').split(',')
				self.screen = Screen(self.action['res_model'], view_type=mode, context=self.context, view_ids = view_id, domain=self.domain, parent = self )
				loadUi( common.uiPath('paned.ui'), self  )
				self.group.setTitle( QString( attrs['string'] or "" )) #ANGEL TODO:  or   self.screen.current_view.title
				layout = QVBoxLayout( )
				layout.addWidget( self.screen )
				self.group.setLayout( layout )

				self.connect( self.pushSearch, SIGNAL( 'clicked()' ), self.slotSearch )
				self.connect( self.pushSwitchView, SIGNAL( 'clicked()'), self.slotSwitch )
				self.connect( self.pushOpen, SIGNAL( 'clicked()' ), self.slotOpen )

				self.setSizePolicy( QSizePolicy.Expanding , QSizePolicy.Expanding )

			elif self.action['view_type']=='tree':
				pass #TODO

	def sizeHint( self ):
		return QSize( 200, 400 )

	def slotSwitch( self ):
		self.screen.switchView()

	def slotSearch( self ):
		win = win_search(self.action['res_model'], domain=self.domain, context=self.context)
		win.exec_()
 		if win.result:
 			self.screen.clear()
 			self.screen.load(win.result)

	def slotOpen( self ):
		obj = service.LocalService('action.main')
		obj.execute(self.act_id , {})

	def store(self):
		self.screen.current_view.store()

	def showValue(self):
		res_id = rpc.session.execute('/object', 'execute', self.action['res_model'], 'search', self.domain)
		self.screen.clear()
		self.screen.load(res_id)
