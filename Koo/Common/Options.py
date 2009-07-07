##############################################################################
#
# Copyright (c) 2004 TINY SPRL. (http://tiny.be) All Rights Reserved.
#                    Fabien Pinckaers <fp@tiny.Be>
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

import ConfigParser, optparse
import os
import sys
import gettext
from Koo import Rpc
import Debug
from PyQt4.QtCore import QDir, QUrl

## @brief The ConfigurationManager class handles Koo settings information. 
# Those settings can be specified in the command line, .koorc configuration file
# or koo server module.
class ConfigurationManager(object):
	## @brief Constructs a ConfigurationManager object.
	# If fileName is specified, the given file name will be used to store and retrive
	# configuration. Otherwise, a standard location will be used.
	def __init__(self, fileName=None):
		self.options = {
			'login.db': 'test',
			'login.url': 'http://admin@localhost:8069',
			'path.share': os.path.join(sys.prefix, 'share/Koo/'),
			'path.pixmaps': os.path.join(sys.prefix, 'share/pixmaps/Koo/'),
			'path.ui': os.path.join(sys.prefix, 'share/Koo/ui'), 
			'tip.autostart': False,
			'tip.position': 0,
			'print_directly': False,
			'client.default_path': os.path.expanduser('~'),
			'stylesheet' : '',
			'tabs_position' : 'top',
			'tabs_closable' : True,
			'show_toolbar' : True,
			'sort_mode' : 'all_items',
			'pos_mode' : False,
			'kde.enabled' : True,
			'attachments_dialog' : False,
		}
		parser = optparse.OptionParser()
		parser.add_option("-c", "--config", dest="config",help=_("specify alternate config file"))
		parser.add_option("-u", "--url", dest="url", help=_("specify the server (ie. http://admin@localhost:8069)"))
		parser.add_option("", "--stylesheet", dest="stylesheet", help=_("specify stylesheet to apply"))
		parser.add_option("", "--pos-mode", action="store_true", default=False, dest="pos_mode", help=_("use POS (Point of Sales) mode"))
		(opt, args) = parser.parse_args()

		self.rcfile = fileName or opt.config or os.environ.get('TERPRC') or os.path.join(self.homeDirectory(), '.koorc')
		self.load()

		if opt.url:
			self.options['login.url'] = opt.url
		if 'login.url' in self.options:
			url = QUrl( self.options['login.url'] )
			if url.isValid():
				self.options['login.server'] = unicode( url.host() )
				self.options['login.port'] = unicode( url.port() )
				self.options['login.protocol'] = '%s://' % url.scheme() 
				self.options['login.login'] = unicode( url.userName() )

		self.options['stylesheet'] = opt.stylesheet
		self.options['pos_mode'] = opt.pos_mode

	def homeDirectory(self):
		return unicode(QDir.toNativeSeparators(QDir.homePath()))

	## @brief Stores current settings in the appropiate config file.
	def save(self):
		try:
			p = ConfigParser.ConfigParser()
			sections = {}
			for o in self.options.keys():
				if not len(o.split('.'))==2:
					continue
				osection,oname = o.split('.')
				if not p.has_section(osection):
					p.add_section(osection)
				p.set(osection,oname,self.options[o])
			p.write(file(self.rcfile,'wb'))
		except:
			Debug.warning( 'Unable to write config file %s !' % self.rcfile )
		return True

	## @brief Loads settings from the appropiate config file.
	def load(self):
		try:
			self.rcexist = False
			if not os.path.isfile(self.rcfile):
				self.save()
				return False
			self.rcexist = True

			p = ConfigParser.ConfigParser()
			p.read([self.rcfile])
			for section in p.sections():
				for (name,value) in p.items(section):
					if value=='True' or value=='true':
						value = True
					if value=='False' or value=='false':
						value = False
					self.options[section+'.'+name] = value
		except Exception, e:
			Debug.warning( 'Unable to read config file %s !' % self.rcfile )
		return True

	def __setitem__(self, key, value):
		self.options[key]=value

	def __getitem__(self, key):
		return self.options[key]

	def get(self, key, defaultValue):
		return self.options.get(key, defaultValue)

	## @brief Tries to load settings from koo server module.
	# If the module is not installed, no exception or error is thrown.
	def loadSettings(self):
		try:
			settings = Rpc.session.call( '/object', 'execute', 'nan.koo.settings', 'get_settings' )
		except:
			settings = {}
		self.options.update( settings )
		Rpc.ViewCache.exceptions = self.options.get('cache_exceptions', [])

options = ConfigurationManager()

