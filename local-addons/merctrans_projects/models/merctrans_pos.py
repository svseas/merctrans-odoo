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
    # Detail po
    """
        Field and API Decorate
    """
    # NOTE: NON-inherit from project page
    purchase_order = fields.Char('Purchase Order', default='Purchase Order')
    contributor = fields.Many2one('res.users', 'Contributor', required=True)
    address = fields.Char('Address',
                          store=True,
                          readonly=True,
                          compute='_get_street_contributor')
    contributor_id = fields.Char('Id',
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
    payment_status = fields.Selection(string='Payment Status',
                                      selection=payment_status_list,
                                      default='unpaid')

    po_value = fields.Float("Project Value",
                            compute="_compute_po_value",
                            store=True,
                            readonly=True,
                            default=0)
    po_status = fields.Selection(string='Status', selection=po_status_list, default='Unpaid')
    service = fields.Many2one('merctrans.services', string='Service')
    # NOTE: INHERIT FROM PROJECT
    source_language = fields.Char('Source Language',
                                  store=True,
                                  compute='_get_project_source',
                                  readonly=True)
    target_language = fields.Char('Target Language',
                                  readonly=True,
                                  compute='_get_project_target')
    currency_id = fields.Many2one('res.currency', string='Currency')
    valid_date = fields.Char('Valid Date',
                             readonly=True,
                             compute='_get_project_valid_date')
    start_date = fields.Date(
        string='Start Date')  #, default="_get_start_date")
    due_date = fields.Date(string='Due Date')  #, default="_get_due_date")

    #  TODO: code = auto gen code unique

    # From Projects?
    project_id = fields.Many2one('merctrans.projects',
                                 string="Project",
                                 store=True)

    # Get contributor address
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
            project.contributor_id = project.contributor.id

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_project_source(self):
        self.source_language = self.project_id.source_language

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
            if project.project_id.start_date:
                project.valid_date = f"{project.project_id.start_date} >> {project.project_id.due_date}"
            else:
                project.valid_date = "Choose Project"
            return project.valid_date

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_project_target(self):
        for project in self:
            project.target_language = project.project_id.target_language

    # po start date must greater than project start date
    @api.depends('project_id')
    @api.constrains('start_date', 'project_id')
    def _start_date_contrains(self):
        for project in self:
            if project.start_date < project.project_id.start_date:
                raise ValidationError(
                    f'Start date must be greater than project start date: {project.project_id.start_date}'
                )

    # po due date must lesser project due date
    @api.depends('project_id')
    @api.constrains('due_date', 'project_id')
    def _due_date_contrains(self):
        for project in self:
            print(project.due_date, project.project_id.due_date)
            if project.due_date > project.project_id.due_date:
                raise ValidationError(
                    f'Start date must be lesser than project start date: {project.project_id.due_date}'
                )

    @api.constrains('start_date', 'due_date')
    def _constraint_date(self):
        for project in self:
            if project.start_date > project.due_date:
                raise ValidationError(
                    'Due date must be greater than Start date!')

    # workunit
    @api.onchange('volume', 'rate_per_work_unit')
    @api.depends('volume', 'sale_rate_per_work_unit')
    def _compute_po_value(self):
        for project in self:
            project.po_value = (
                100 -
                0) / 100 * project.volume * project.sale_rate_per_work_unit
