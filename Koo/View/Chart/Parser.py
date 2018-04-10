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

modules = {}
errors = {}

import locale
from Koo.Common import Common

from ChartView import *
from ChartGraphicsView import *

import sys

from Koo.View.AbstractParser import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *


class ChartParser(AbstractParser):

    def create(self, viewId, parent, viewModel, node, fields):
        self.viewModel = viewModel
        self.parent = parent

        attrs = Common.nodeAttributes(node)

        # Create the view
        self.view = ChartView(parent)
        self.view.id = viewId
        self.view.title = attrs.get('string', _('Unknown'))
        self.view.model = self.parent.currentRecord()

        widget, onWriteFunction = self.parse(
            self.parent.currentRecord(), node, fields, self.view)
        self.view.setWidget(widget)
        self.view.setOnWriteFunction(onWriteFunction)

        return self.view

    def parse(self, model, root_node, fields, container):
        attrs = Common.nodeAttributes(root_node)
        self.title = attrs.get('string', 'Unknown')

        onWriteFunction = ''

        axis = []
        groups = []
        axis_data = {}
        for node in root_node.childNodes:
            if node.localName == 'field':
                node_attrs = Common.nodeAttributes(node)
                if node_attrs.get('group', False):
                    groups.append(str(node_attrs['name']))
                else:
                    axis.append(str(node_attrs['name']))
                axis_data[str(node_attrs['name'])] = node_attrs

        #
        # TODO: parse root_node to fill in axis
        #

        chart = ChartGraphicsView(container)
        chart.setModel(self.parent.currentRecord())
        chart.setType(attrs.get('type', 'pie'))
        chart.setAxis(axis)
        chart.setGroups(groups)
        chart.setFields(fields)
        chart.setAxisData(axis_data)
        if attrs.get('orientation', 'vertical') == 'vertical':
            chart.setOrientation(Qt.Vertical)
        else:
            chart.setOrientation(Qt.Horizontal)

        return chart, onWriteFunction


# vim:noexpandtab:
