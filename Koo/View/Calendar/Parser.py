##############################################################################
#
# Copyright (c) 2008 Albert Cervera i Areny <albert@nan-tic.com>
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

from Koo.Model.KooModel import *
from Koo.View.AbstractParser import *
from Calendar import *

from PyQt4.QtCore import *
from PyQt4.QtGui import *


class CalendarParser(AbstractParser):

    def create(self, viewId, parent, model, rootNode, fields):
        self.screen = parent
        view = CalendarView(parent)
        view.id = viewId

        attrs = Common.nodeAttributes(rootNode)
        view.setOnWriteFunction(attrs.get('on_write', ''))

        if not view.title:
            view.title = attrs.get('string', _('Unknown'))

        startDate = attrs.get('date_start')
        stopDate = attrs.get('date_stop')
        dateDelay = attrs.get('date_delay')
        color = attrs.get('color')

        header = []
        header.append(startDate)
        if dateDelay:
            header.append(dateDelay)
        if color:
            header.append(color)
        for node in rootNode.childNodes:
            node_attrs = Common.nodeAttributes(node)
            if node.localName == 'field':
                header.append(node_attrs['name'])

        # <calendar string="Tasks" date_start="date_start" date_delay="planned_hours" color="user_id">
        #	<field name="name"/>
        #	<field name="project_id"/>
        # </calendar>

        model = KooModel(view)
        model.setMode(KooModel.ListMode)
        model.setRecordGroup(self.screen.group)
        model.setFields(fields)
        model.setFieldsOrder(header)
        model.setReadOnly(not attrs.get('editable', False))
        model.setShowBackgroundColor(True)

        view.setReadOnly(not attrs.get('editable', False))
        view.setModel(model)
        view.setModelDateColumn(0)
        column = 1
        if dateDelay:
            view.setModelDurationColumn(column)
            column += 1
        if color:
            view.setModelColorColumn(column)
            column += 1
        view.setModelTitleColumn(column)

        return view

# vim:noexpandtab:
