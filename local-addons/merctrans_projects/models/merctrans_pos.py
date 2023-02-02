from odoo.exceptions import ValidationError

from odoo import api, fields, models


class MerctransPOs(models.Model):
    """
        Khoi tao model
    """
    _name = 'merctrans.pos'
    _description = "Purchase Order by Projects"
    _rec_name = "purchase_order"
    """
        Static List
    """
    po_status_list = [('in progress', 'In Progress'),
                      ('completed', 'Completed'), ('canceled', 'Canceled')]

    work_unit_list = [('word', 'Word'), ('hour', 'Hour'), ('page', 'Page'),
                      ('job', 'Job')]

    payment_status_list = [('unpaid', 'Unpaid'), ('invoiced', 'Invoiced'),
                           ('paid', 'Paid')]

    language_list = [('zh-CN', 'Chinese (Simplified)'),
                     ('zh-TW', 'Chinese (Traditional)'),
                     ('en-US', 'English   (US)'), ('en-GB', 'English (UK)'),
                     ('fr-FR', 'French'), ('it-IT', 'Italian'),
                     ('es-ES', 'Spanish (Spain)'),
                     ('es-AR', 'Spanish (Argentina)'),
                     ('es-LA', 'Spanish (Latin America)'), ('th-TH', 'Thai'),
                     ('tr-TR', 'Turkish'), ('vi-VN', 'Vietnamese'),
                     ('ko-KR', 'Korean'), ('ja-JP', 'Japanese'),
                     ('ru-RU', 'Russian'), ('de-DE', 'German (Germany)'),
                     ('de-AT', 'German (Austria)'),
                     ('de-CH', 'German (Switzerland)')]
    # Detail po
    """
        Field and API Decorate
    """
    # NOTE: NON-inherit from project page

    purchase_order = fields.Char('Purchase Order',
                                 store=True,
                                 readonly=True,
                                 compute="_get_purchase_order")

    contributor = fields.Many2one('merctrans.contributors',
                                  'Contributor*',
                                  required=True)

    address = fields.Char('Address',
                          store=True,
                          readonly=True,
                          compute='_get_street_contributor')

    project_id = fields.Many2one('merctrans.projects',
                                 string="Project",
                                 store=True)
    contributor_id = fields.Integer('Id',
                                    store=True,
                                    readonly=True,
                                    compute='_get_id_contributor')

    contributor_email = fields.Char('Email',
                                    store=True,
                                    readonly=True,
                                    compute='_get_email_contributor')

    work_unit = fields.Selection(string='Work Unit*',
                                 selection=work_unit_list,
                                 required=True)

    volume = fields.Integer(string='Volume*', required=True, default=0)

    sale_rate_per_work_unit = fields.Float(string='Rate*',
                                           required=True,
                                           default=0)

    payment_status = fields.Selection(string='Payment Status*',
                                      selection=payment_status_list,
                                      required=True,
                                      default='unpaid')

    po_value = fields.Float("Value",
                            compute="_compute_po_value",
                            store=True,
                            readonly=True,
                            default=0)

    po_status = fields.Selection(string='Status*',
                                 selection=po_status_list,
                                 required=True,
                                 default='in progress')

    service = fields.Many2one('merctrans.services', string='Service')

    # NOTE: INHERIT FROM PROJECT

    source_language = fields.Selection(string="Source Languages",
                                      selection=language_list)

    target_language = fields.Selection(string="Target Language",
                                       selection=language_list)

    currency_id = fields.Char('Currency', compute='_get_contributor_currency')

    valid_date = fields.Char('Valid Date',
                             readonly=True,
                             compute='_get_project_valid_date')

    start_date = fields.Date(string='Start Date*',
                             required=True,
                             default=fields.Date.today())

    due_date = fields.Date(string='Due Date*',
                           required=True,
                           default=fields.Date.today())
    # default=lambda self: self.env['merctrans.projects'].search([(
    #     'project_id', '=', self.project_id.project_id)]).due_date)

    # From Projects?

    # Get contributor currency
    @api.onchange('contributor')
    @api.depends('contributor')
    def _get_contributor_currency(self):
        # TODO: Test this, why currency always fail
        # print(self.contributor)
        # print(self.contributor.currency)
        # self.ensure_one()
        # print(self.contributor.currency)
        # self.currency_id = self.contributor.currency.name

        for po in self:
            if po.contributor:
                po.currency_id = po.contributor.currency.name
            else:
                po.currency_id = "Select Contributor"



    # Get contributor address
    @api.onchange('project_id', 'contributor')
    @api.depends('project_id', 'contributor')
    def _get_purchase_order(self):
        for po in self:
            if po.project_id:
                pj = po.project_id.project_id
                ctrb = po.contributor.name if po.contributor else "ctrb"
                ids = len(po.project_id.po_details)
                po.purchase_order = f"PO{ids:03d}-{ctrb[:3].upper()}|{pj}"
            else:
                po.purchase_order = "Select Project"

    @api.onchange('contributor')
    @api.depends('contributor')
    def _get_street_contributor(self):
        self.ensure_one()
        print(self.contributor.street)
        self.address = self.contributor.street

    # Get api email
    @api.onchange('contributor')
    @api.depends('contributor')
    def _get_email_contributor(self):
        for project in self:
            print(project.contributor.email)
            project.contributor_email = project.contributor.email

    @api.onchange('contributor')
    @api.depends('contributor')
    def _get_id_contributor(self):
        for project in self:
            print(project.contributor.id)
            project.contributor_id = project.contributor.user_id

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_project_source(self):
        for po in self:
            if po.project_id.source_language:
                po.source_language = po.project_id.source_language
            else:
                po.source_language = "Choose Project"

    # @api.onchange('project_id')
    # @api.depends('project_id')
    # def _get_start_date(self):
    #     for project in self:
    #         if project.project_id.start_date:
    #             return project.project_id.start_date
    #
    # @api.onchange('project_id')
    # @api.depends('project_id')
    # def _get_due_date(self):
    #     for project in self:
    #         if project.project_id.start_date:
    #             return project.project_id.due_date

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_project_valid_date(self):
        for project in self:
            if project.project_id:
                project.valid_date = f"{project.project_id.start_date} >> {project.project_id.due_date}"
            else:
                project.valid_date = "Choose Project"

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_project_target(self):
        for po in self:
            if po.project_id.target_language:
                po.target_language = po.project_id.target_language
            else:
                po.target_language = 'Choose Project'

    @api.constrains('volume')
    def _volume_contrains(self):
        for po in self:
            if int(po.volume) == 0:
                raise ValidationError(f"PO: {po.purchase_order} \nContributor: {po.contributor.name}\nFAIL!!! \nVolume must greater than 0")


    # po start date must greater than project start date
    # @api.depends('project_id')
    # @api.constrains('start_date', 'project_id')
    # def _start_date_contrains(self):
    #     for project in self:
    #         if project.start_date < project.project_id.start_date:
    #             raise ValidationError(
    #                 f'Start date must be greater than project start date: {project.project_id.start_date}'
    #             )

    # po due date must lesser project due date
    # @api.depends('project_id')
    # @api.constrains('due_date', 'project_id')
    # def _due_date_contrains(self):
    #     for project in self:
    #         print(project.due_date, project.project_id.due_date)
    #         if project.due_date > project.project_id.due_date:
    #             raise ValidationError(
    #                 f'Start date must be lesser than project start date: {project.project_id.due_date}'
    #             )

    @api.constrains('start_date', 'due_date')
    def _constraint_date(self):
        for po in self:
            if po.start_date > po.due_date:
                raise ValidationError(
                    f'PO: {po.purchase_order} \nContributor: {po.contributor.name}\nFAIL!!\nDue date must be after Start date!')

    @api.constrains("sale_rate_per_work_unit")
    def _constraint_sale_rate(self):
        for po in self:
            if po.sale_rate_per_work_unit == 0:
                raise ValidationError(
                    f'PO: {po.purchase_order} \nContributor: {po.contributor.name}\nFAIL!!\nSale rate must be greater than 0!'
                )

    # workunit
    @api.onchange('volume', 'sale_rate_per_work_unit')
    @api.depends('volume', 'sale_rate_per_work_unit')
    def _compute_po_value(self):
        for project in self:
            project.po_value = (
                100 -
                0) / 100 * project.volume * project.sale_rate_per_work_unit


    def action_send_email(self):
        mail_template_id = self.env.ref("merctrans_projects.pos_confirm_email").id
        template = self.env["mail.template"].browse(mail_template_id)
        template.send_mail(self.id, force_send=True)