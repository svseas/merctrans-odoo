from odoo.exceptions import ValidationError

from odoo import api, fields, models


class MerctransClient(models.Model):
    _name = 'merctrans.clients'
    _rec_name = 'name'
    _inherit = 'res.partner'
    _description = "Merctrans's Partner"
    channel_ids = fields.Many2many('res.partner',
                                   'relation_m2m_table',
                                   'rel_1',
                                   'rel_2',
                                   string='Partners')
    client_note = fields.Html('Client note')
    client_currency = fields.Many2one('res.currency',
                                      string="Currency",
                                      required=True)
