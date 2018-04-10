##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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

from Koo.Common import Api
from Koo.Common import Common
from Koo.Plugins import Plugins
from Koo import Rpc

# @brief Opens a new window that allows setting the rating for the current document.


def semantic(model, id, ids, context):
    model_id = Rpc.session.execute(
        '/object', 'execute', 'ir.model', 'search', [('model', '=', model)], 0, 0, False, context)
    ctx = context.copy()
    ctx['subject_model'] = model
    ctx['subject_id'] = id
    domain = [
        ('subject_model', '=', model_id),
        ('subject_id', '=', id)
    ]
    Api.instance.createWindow(
        None, 'nan.semantic.triple', mode='tree,form', domain=domain, context=ctx)


if Common.isKdeAvailable:
    Plugins.register('Semantic', '.*', _('Semantic Info'), semantic)
