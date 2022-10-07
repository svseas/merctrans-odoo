# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.exceptions import ValidationError

from odoo import api, fields, models
# <field name="project_id" />
#                     <field name="project_name" />
#                     <field name="client_po_number"/>
#                     <field name="volume" />
#                     <field name="sale_rate" />
# <!--                    <field name="discount" />-->
#                     <field name="project_value" />
#                     <field name="currency_id" />
#                     <field name="payment_status" />

class MercTransInvoices(models.Model):
    _name = 'merctrans.sale'
    _rec_name = 'sale_order_name'
    _description = 'MercTrans Sale Orders for Project Managers'

    status_list = [('invoiced', 'Invoiced'), ('paid', 'Paid'),
                   ('unpaid', 'Unpaid')]

    project_id = fields.Many2one('merctrans.projects',
                                 string="Project",
                                 store=True)
    sale_order_name = fields.Char(string="Sale Order Name")

    client = fields.Char(string='Client',
                         readonly=True,
                         compute = "_get_client_name")

    client_po_number = fields.Char(string='Client PO number',
                                   readonly=True,
                                   compute="_get_client_po_number")

    sale_order_volume = fields.Integer(string='Volume*',
                                       required=True,
                                       default=0)

    sale_rate = fields.Float(string='Rate*',
                             readonly=True,
                             compute="_get_sale_rate")

    currency_id = fields.Char(string='Currency',
                              readonly=True,
                              compute="_get_currency_id")


    # The next section is to automatically populate field when a project is selected.
    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_client_name(self):
        for sale_order in self:
            if sale_order.project_id.client_name:
                sale_order.client = sale_order.project_id.client_name

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_client_po_number(self):
        for sale_order in self:
            if sale_order.project_id.client_po_number:
                sale_order.client_po_number = sale_order.project_id.client_po_number
            else:
                sale_order.client_po_number = " "

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_currency_id(self):
        for sale_order in self:
            if sale_order.project_id.currency_id:
                sale_order.currency_id = sale_order.project_id.currency_id

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_sale_rate(self):
        for sale_order in self:
            if sale_order.project_id.sale_rate:
                sale_order.sale_rate = sale_order.project_id.sale_rate
