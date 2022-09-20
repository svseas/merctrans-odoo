# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.exceptions import ValidationError

from odoo import api, fields, models


class MercTransSaleOrder(models.Model):
    _name = 'merctrans.so'
    _rec_name = 'sale_order_name'
    _description = 'MercTrans Sale Orders for Project Managers'

    status_list = [('invoiced', 'Invoiced'), ('paid', 'Paid'),
                   ('unpaid', 'Unpaid')]

    sale_order_id = fields.Integer('Invoice ID',
                                index=True,
                                store=True,
                                readonly=True,
                                default=lambda self: self.env['ir.sequence'].
                                next_by_code('increment_invoice_id'))
    sale_order_name = fields.Char(string='Sale Order #', compute="_get_sale_order_name")
    sale_order_date = fields.Date(string='Issue Date*', default=datetime.today(), required=True)
    sale_order_due_date = fields.Date(string='Due Date*', required=True)
    sale_order_client = fields.Many2one('merctrans.clients',
                                     string='Client',
                                     required='True')
    client_name = fields.Char(compute="_get_invoice_client")

    sale_order_job = fields.Many2one('merctrans.projects',
                                           string='Sale Order Job')
    currency_id = fields.Many2one('res.currency', string='Currency')
    sale_order_value = fields.Float("Sub Total",
                                 compute="_compute_invoice_value")
    sale_order_status = fields.Selection(string="Invoice Status",
                                      selection=status_list,
                                      default='unpaid')
    sale_order_total = fields.Float('Total', compute="_compute_sale_order_total", store=True, readonly=True, default=0)


    @api.onchange('sale_order_total')
    @api.depends('invoice_value', 'invoice_total', 'discount')
    def _compute_invoice_total(self):
        for sale_order in self:
            sale_order.sale_order_total = (100 - invoice.discount) / 100 * invoice.invoice_value


    @api.depends('invoice_client')
    @api.onchange('invoice_client')
    def _get_invoice_client(self):
        self.client_name = ''
        for inv in self:
            if inv.invoice_client:
                inv.client_name += inv.invoice_client.name
            else:
                inv.client_name = 'default'


    @api.depends('invoice_client', 'invoice_id')
    @api.onchange('invoice_client', 'invoice_id')
    def _get_invoice_name(self):
        for inv in self:
            if inv.invoice_client:
                cl_name = "".join(inv.invoice_client.name.split()).upper()
            else:
                cl_name = "CLIE"
            inv.invoice_name = f"INV{inv.invoice_id:05d}-{cl_name[:4]}-{fields.Date.today().strftime('%y%m%d')}"






    @api.constrains('invoice_paid_date','invoice_date', 'invoice_status')
    def paid_date_constrains(self):
        for inv in self:
            if inv.invoice_paid_date and inv.invoice_paid_date < inv.invoice_date:
                raise ValidationError('Invoice paid date cannot be before invoice due date')
            if inv.invoice_status != 'paid' and inv.invoice_paid_date:
                raise ValidationError('Cannot have paid date when status is not Paid')

    @api.constrains('invoice_details_ids')
    def invoice_detail_constrains(self):
        for inv in self:
            if not inv.invoice_details_ids:
                raise ValidationError('Invoice must have at least one project!')

    @api.constrains('invoice_details_ids', 'invoice_status')
    def invoice_status_constrains(self):
        for inv in self:
            if not inv.invoice_details_ids and inv.invoice_status:
                raise ValidationError('Cannot set invoice status when there is no job!')

    # @api.model
    # def create(self, vals):
    #     print("Invoices Create Vals ", vals)
    #     return super(MercTransInvoices, self).create(vals)
    #
    # def write(self, vals):
    #     print("Invoices Write Vals ", vals)
    #     return super(MercTransInvoices, self).write(vals)

    # @api.onchange('invoice_status')
    # def sync_status(self):
    #
    #     for project in self.invoice_details_ids:
    #         if self.invoice_status == 'paid':
    #             project.write({'payment_status': 'paid'})
    #         if self.invoice_status == 'invoiced':
    #             project.write({'payment_status': 'invoiced'})
    #         if self.invoice_status == 'unpaid':
    #             project.write({'payment_status': 'unpaid'})
    #         if not self.invoice_status:
    #             project.write({'payment_status': 'unpaid'})
    #
    # @api.ondelete(at_uninstall=False)
    # def _check_invoice_status(self):
    #     for rec in self:
    #         if rec.invoice_status:
    #             raise ValidationError("You cannot delete an invoice with invoice status set!")