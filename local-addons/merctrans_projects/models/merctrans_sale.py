# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.exceptions import ValidationError

from odoo import api, fields, models


class MercTransInvoices(models.Model):
    _name = 'merctrans.sale'
    _rec_name = 'sale_order_name'
    _description = 'MercTrans Sale Orders for Project Managers'

    status_list = [('invoiced', 'Invoiced'), ('paid', 'Paid'),
                   ('unpaid', 'Unpaid')]

    project_id = fields.Many2one('merctrans.projects',
                                 string="Project",
                                 store=True)
    sale_order_name = fields.Char(string="Sale Order")



