from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MercTransInvoices(models.Model):
    _name = 'merctrans.invoices'
    _rec_name = 'invoice_name'
    _description = 'MercTrans Invoices for Project Managers'


invoice_id = fields.Integer('Invoices ID')
invoice_name = fields.Char ('Invoices name')
invoice_date = fields.Date(string='Invoice Date')
invoice_client = fields.Many2many('res.partner', string='Client', required='True')
invoice_details = fields.One2many('merctrans.invoices.lines', 'job_id', string="Invoice Lines")


class MercTransInvoicesLines(models.Model):
    _name = 'merctrans.invoices.lines'
    _description = "Merctrans Invoices Lines"

    job_id = fields.Many2one('merctrans.projects', string='Job')
    job_qty = fields.Integer(string='Quantity')
