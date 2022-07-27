import re
from odoo.exceptions import ValidationError
from odoo import api, fields, models


class MerctransClient(models.Model):

    _name = 'merctrans.contributors'

    _rec_name = 'name'

    _description = "Merctrans's Contributors"
    _inherits = {'res.users': 'user_id'}

    # partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True,
    #                              string='Related Partner', help='Partner-related data of the user')
    user_id = fields.Many2one('res.users', required=True, ondelete='cascade')

    country = fields.Many2one('res.country', string='Country')
    currency = fields.Many2one('res.currency', 'Currency')

    contributor_note = fields.Html('Client note')

    phone_number = fields.Char(string='Phone number')

    pos_history = fields.One2many('merctrans.pos',
                                  'contributor',
                                  readonly=True)

    total_po = fields.Integer('Total PO',
                              readonly=True,
                              compute="_get_total_po")


    def _get_total_po(self):
        for contributor in self:
            if contributor.pos_history:
                contributor.total_po = len(contributor.pos_history)
            else:
                contributor.total_po = 0

    @api.constrains('name')
    def check_duplicate_name(self):
        for contributor in self:
            contributor = self.env['merctrans.pos'].search([
                ('name', '=', self.name), ('id', '!=', self.id)
            ])
            if contributor:
                raise ValidationError('Contributor name cannot be duplicated!')

    @api.constrains('email')
    def validate_email(self):
        if self.email:
            match = re.match(
                '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                self.email)
            if match is None:
                raise ValidationError('Not a valid email')
