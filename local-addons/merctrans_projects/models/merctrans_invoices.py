# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.exceptions import ValidationError

from odoo import api, fields, models


class MercTransInvoices(models.Model):
    _name = 'merctrans.invoices'
    _rec_name = 'invoice_name'
    _description = 'MercTrans Invoices for Project Managers'

    status_list = [('invoiced', 'Invoiced'), ('paid', 'Paid'),
                   ('unpaid', 'Unpaid')]

    invoice_id = fields.Integer('Invoice ID',
                                index=True,
                                store=True,
                                readonly=True,
                                default=lambda self: self.env['ir.sequence'].
                                next_by_code('increment_invoice_id'))
    invoice_name = fields.Char('Invoice name', compute="_get_invoice_name")
    invoice_date = fields.Date(string='Invoice Date')
    invoice_client = fields.Many2one('merctrans.clients',
                                     string='Client',
                                     required='True')
    invoice_details_ids = fields.Many2many('merctrans.projects',
                                           string='Invoice Lines')
    currency_id = fields.Many2one('res.currency', string='Currency')
    invoice_value = fields.Float("Invoice Value",
                                 compute="_compute_invoice_value")
    invoice_status = fields.Selection(string="Invoice Status",
                                      selection=status_list,
                                      default='Unpaid')

    @api.depends('invoice_client', 'invoice_id')
    @api.onchange('invoice_client', 'invoice_id')
    def _get_invoice_name(self):
        for inv in self:
            if inv.invoice_client:
                cl_name = "".join(inv.invoice_client.name.split()).upper()
            else:
                cl_name = "CLIE"
            inv.invoice_name = f"INV{inv.invoice_id:05d}-{cl_name[:4]}-{fields.Date.today().strftime('%y%m%d')}"

    @api.depends('invoice_details_ids')
    def _compute_invoice_value(self):
        for item in self:
            item.invoice_value = sum(line.project_value  # x??? rename plz
                                     for line in item.invoice_details_ids)

    @api.constrains('invoice_details_ids', 'currency_id')
    def currency_constrains(self):
        for job in self:
            for x in job.invoice_details_ids:
                if job.currency_id != x.currency_id:
                    raise ValidationError(
                        'Job currency must be the same as invoice currency!')

    # @api.model
    # def create(self, vals):
    #     print("Invoices Create Vals ", vals)
    #     return super(MercTransInvoices, self).create(vals)
    #
    # def write(self, vals):
    #     print("Invoices Write Vals ", vals)
    #     return super(MercTransInvoices, self).write(vals)

    @api.onchange('invoice_status')
    def sync_status(self):

        for project in self.invoice_details_ids:
            if self.invoice_status == 'paid':
                project.write({'payment_status': 'paid'})
            if self.invoice_status == 'invoiced':
                project.write({'payment_status': 'invoiced'})