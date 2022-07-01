from odoo.exceptions import ValidationError

from odoo import api, fields, models


class MerctransClient(models.Model):
    _name = 'merctrans.clients'
    _rec_name = 'name'
    _inherits = {'res.partner':'partner_id'}
    _description = "Merctrans's Partner"

    # partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True,
    #                              string='Related Partner', help='Partner-related data of the user')
    name = fields.Char(related='partner_id.name', inherited=True, readonly=False)
    email = fields.Char(related='partner_id.email', inherited=True, readonly=False)
    client_note = fields.Html('Client note')
    # client_currency = fields.Many2one('res.currency',
    #                                   string="Currency",)
