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

    status = fields.Selection(string="Sale Order Status",
                              selection=status_list,
                              default='unpaid',
                              readonly=True,
                              store=True)

    client = fields.Char(string='Client',
                         readonly=True,
                         compute="_get_client_name")

    client_po_number = fields.Char(string='Client PO number',
                                   readonly=True,
                                   compute="_get_client_po_number")

    volume = fields.Integer(string='Volume*',
                            required=True,
                            compute="_get_volume",
                            inverse="_inverse_get_volume",
                            store=True)

    sale_rate = fields.Float(string='Rate*',
                             readonly=True,
                             compute="_get_sale_rate")

    currency_id = fields.Many2one('res.currency',
                                  string='Currency*',
                                  required=True)

    discount = fields.Integer(string='Discount (%)',
                              compute="_get_discount",
                              inverse="_inverse_get_discount")

    value = fields.Float(string="Sale Order Value",
                         readonly=True,
                         compute="_compute_sale_order_value")

    # The next section is to automatically populate field when a project is selected.
    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_client_name(self):
        for sale_order in self:
            if sale_order.project_id.client_name:
                sale_order.client = sale_order.project_id.client_name
            else:
                sale_order.client = " "

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
    def _get_sale_rate(self):
        for sale_order in self:
            if sale_order.project_id.sale_rate:
                sale_order.sale_rate = sale_order.project_id.sale_rate
            else:
                sale_order.sale_rate = 0

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_volume(self):
        for sale_order in self:
            if sale_order.project_id.volume:
                sale_order.volume = sale_order.project_id.volume
            else:
                sale_order.volume = 0

    def _inverse_get_volume(self):
        return

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_discount(self):
        for sale_order in self:
            if sale_order.project_id.discount:
                sale_order.discount = sale_order.project_id.discount

    def _inverse_get_discount(self):
        return

    @api.onchange('volume', 'sale_rate')
    @api.depends('volume', 'sale_rate', 'discount')
    def _compute_sale_order_value(self):
        for sale_order in self:
            sale_order.value = (100 - sale_order.discount) / 100 * sale_order.volume * sale_order.sale_rate

    @api.ondelete(at_uninstall=False)
    def _check_status(self):
        for sale_order in self:
            if sale_order.status == "paid":
                raise ValidationError("You cannot delete a sale order with invoice status set to Paid!")
