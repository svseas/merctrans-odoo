from odoo.exceptions import ValidationError

from odoo import api, fields, models


class MerctransJobs(models.Model):
    _name = 'merctrans.jobs'
    _description = "Jobs by Projects"
    _rec_name = "title"
    project_status_list = [('potential', 'Potential'),
                           ('confirmed', 'Confirmed'),
                           ('in progress', 'In Progress'), ('in qa', 'In QA'),
                           ('delivered', 'Delivered'),
                           ('canceled', 'Canceled')]

    # Detail Job

    title = fields.Char('Job Title', default='Job Title')
    pic = fields.Many2one('res.users', 'PIC', required=True)
    address = fields.Char('Address',
                          store=True,
                          readonly=True,
                          compute='_get_street_pic')
    pic_id = fields.Char('Id',
                         store=True,
                         readonly=True,
                         compute='_get_id_pic')
    pic_email = fields.Char('Email',
                            store=True,
                            readonly=True,
                            compute='_get_email_pic')
    source_language = fields.Char('Source Language',
                                  default="English",
                                  store=True,
                                  compute='_get_project_source',
                                  readonly=True)
    target_language = fields.Char('Target Language',
                                  default="Vietnamess",
                                  readonly=True,
                                  compute='_get_project_target')
    currency_id = fields.Many2one('res.currency', string='Currency')
    valid_date = fields.Char('Valid Date',
                             default="Choose Project",
                             readonly=True,
                             compute='_get_project_valid_date')
    start_date = fields.Date(string='Start Date')
    due_date = fields.Date(string='Due Date')

    #  TODO: code = auto gen code unique

    # From Projects?
    project_id = fields.Many2one('merctrans.projects',
                                 string="Project",
                                 required=True)
    job_status = fields.Selection(string='JOB STATUS',
                                  selection=project_status_list)

    # Currency - get from partner Currency

    #  TODO: - Cần thêm fields currency cho res.partner

    # TODO: - Cần thêm fields rate cho model -> but? Tính kiểu ?

    # get Source default

    # TODO: Sau khi có currency change street = currency EZ???
    # Get pic address
    @api.onchange('pic')
    @api.depends('pic')
    def _get_street_pic(self):
        self.ensure_one()
        print(self.pic.street)
        self.address = self.pic.street

    # Get api email
    @api.onchange('pic')
    @api.depends('pic')
    def _get_email_pic(self):
        for project in self:
            print(project.pic.email)
            project.pic_email = project.pic.email

    @api.onchange('pic')
    @api.depends('pic')
    def _get_id_pic(self):
        for project in self:
            print(project.pic.id)
            project.pic_id = project.pic.id

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_project_source(self):
        self.source_language = self.project_id.source_language

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_project_valid_date(self):
        for project in self:
            if project.project_id.start_date:
                project.valid_date = f"{project.project_id.start_date} >> {project.project_id.due_date}"
            else:
                project.valid_date = "Choose Project"

    @api.onchange('project_id')
    @api.depends('project_id')
    def _get_project_target(self):
        for project in self:
            project.target_language = project.project_id.target_language

    # Job start date must greater than project start date
    @api.depends('project_id')
    @api.constrains('start_date', 'project_id')
    def _start_date_contrains(self):
        for project in self:
            print(project.start_date, project.project_id.start_date)
            if project.start_date < project.project_id.start_date:
                raise ValidationError(
                    f'Start date must be greater than project start date: {project.project_id.start_date}'
                )

    # Job due date must lesser project due date
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
