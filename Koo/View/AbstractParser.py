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

# @brief The AbstractParser class describes the interface any view parser
# has to implement.
# In ordre to create a view you need to create a Parser. It should
# inherit AbstractParser and provide the following interface:


class AbstractParser(object):

    # @brief You need to provide the create function with the following parameters:
    #    viewId:    Id of the view. The parser is responsible for assigning view.id = viewId.
    #    parent:    Holds the reference to the parent QWidget. Usually screen.
    #               You should make of this the parent of your view.
    #               Note/TODO: As of this writing parent NEEDS TO BE a Screen object
    #               but this requirement should be removed in the near future.
    #    model:     This is the name of the model the view will handle
    #    node:      The node of the XML to process.
    #    fields:    The fields that we want to be shown.
    #
    #   RETURN
    #    widget:    Will hold the View which will inherit AbstractView
    def create(self, viewId, parent, model, node, fields):
        pass
