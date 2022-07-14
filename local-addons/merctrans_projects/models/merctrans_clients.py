import re
from odoo.exceptions import ValidationError
from odoo import api, fields, models


class MerctransClient(models.Model):
    _name = 'merctrans.clients'
    _rec_name = 'name'
    _description = "Merctrans's Clients"

    # partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True,
    #                              string='Related Partner', help='Partner-related data of the user')
    name = fields.Char(string='Client')
    email = fields.Char(string='Email')
    country = fields.Many2one('res.country', string='Country')
    client_note = fields.Html('Client note')
    phone_number = fields.Char(string='Phone number')
    website = fields.Char(string='Website')
    project_history = fields.One2many('merctrans.projects', 'client', readonly=True)
    invoice_history = fields.One2many('merctrans.invoices', 'invoice_client')
    # client_currency = fields.Many2one('res.currency',
    #                                   string="Currency",)

    @api.constrains('name')
    def check_duplicate_name(self):
        for company_rec in self:
            company_rec = self.env['merctrans.clients'].search([('name', '=', self.name), ('id', '!=', self.id)])
            if company_rec:
                raise ValidationError('Company name cannot be duplicated!')

    @api.constrains('email')
    def validate_email(self):
        if self.email:
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', self.email)
        if match == None:
            raise ValidationError('Not a valid email')


