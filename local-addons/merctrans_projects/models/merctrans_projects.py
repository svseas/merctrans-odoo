# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.exceptions import ValidationError

from odoo import api, fields, models


class MercTransServices(models.Model):
    _name = 'merctrans.services'
    _rec_name = 'services_names'
    _description = 'Services offered by MercTrans'

    department_list = [('localization', 'Localization'),
                       ('marketing', 'Marketing'),
                       ('developement', 'Development')]
    department = fields.Selection(string="Department",
                                  selection=department_list)
    services_names = fields.Char('Services')


class MercTransTags(models.Model):
    _name = 'merctrans.tags'
    _rec_name = 'tag'
    _description = 'Project Tags'

    tag = fields.Char(string='Tag', required=True)


class MercTransProjects(models.Model):
    """
        Khởi tạo model
    """
    _name = 'merctrans.projects'
    _description = 'MercTrans Projects'
    _rec_name = 'project_name'
    """
        Static list
    """

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

    work_unit_list = [('word', 'Word'), ('hour', 'Hour'), ('page', 'Page'),
                      ('job', 'Job')]

    project_status_list = [('potential', 'Potential'),
                           ('confirmed', 'Confirmed'),
                           ('in progress', 'In Progress'), ('in qa', 'In QA'),
                           ('delivered', 'Delivered'),
                           ('canceled', 'Canceled')]

    payment_status_list = [('unpaid', 'Unpaid'), ('invoiced', 'Invoiced'),
                           ('paid', 'Paid')]

    # number_id = fields.Integer(string="Stt",
    #                            default=lambda self: self.env['ir.sequence'].
    #                            next_by_code('increment_number_id'))
    # Auto gen number_id
    """
        Field and decorate function, được nhóm chung vào từng section
        để thuận tiện hơn trong chỉnh sửa và debug
    """

    # NOTE: ID and Project ID, project name, client, tags
    number_id = fields.Integer('No number',
                               index=True,
                               readonly=True,
                               copy=False)
    project_id = fields.Char('Project Id',
                             default="new_project",
                             readonly=True,
                             compute="_get_project_id")

    project_name = fields.Char(
        'Project Name*',
        default=lambda self:
        f"Project No {self.env['merctrans.projects'].search_count([])}")

    client = fields.Many2one('merctrans.clients',
                             string='Client*',
                             required=True,
                             default=lambda self: self.env['merctrans.clients']
                             .search([('name', '=', 'merctrans')], limit=1))

    services_ids = fields.Many2many('merctrans.services', string='Services')
    client_name = fields.Char('Client_',
                              compute='_get_client_name',
                              default='merctrans',
                              readonly=True)
    tags = fields.Many2many('merctrans.tags', string='Tags')

    project_manager = fields.Many2one('res.users',
                                      string='Project Manager*',
                                      required=True)
    # compute project_id by client many 2 one -> should default value client_name
    # services contain tags
    # NOTE: Target and Source Language
    source_language = fields.Selection(string="Source Languages",
                                       selection=language_list,
                                       default="Select a language")
    target_language = fields.Selection(string="Target Language",
                                       selection=language_list,
                                       default="Select a language")

    # NOTE: TIME, START and DUE DATE
    current_time = datetime.now().strftime("%Y%m%d-%H%M%s")
    start_date = fields.Date(string='Start Date*', required=True)
    due_date = fields.Date(string='Due Date*', required=True)

    # NOTE: SALE, Volume, unit, rate, margin

    discount = fields.Integer(string='Discount', default=0)
    # add discount field
    # fixed job

    work_unit = fields.Selection(string='Work Unit*',
                                 selection=work_unit_list,
                                 required=True)
    volume = fields.Integer(string='Volume*', required=True, default=0)
    currency_id = fields.Many2one('res.currency',
                                  string='Currency*',
                                  required=True)
    sale_rate = fields.Float(string='Rate*', required=True, default=0)
    project_value = fields.Float("Project Value",
                                 compute="_compute_project_value",
                                 store=True,
                                 readonly=True,
                                 default=0)
    total_po_value = fields.Float("Total PO value",
                                  compute="_compute_po_value",
                                  store=True,
                                  readonly=True,
                                  default=0)
    project_margin = fields.Float("Project Margin",
                                  compute="_compute_margin",
                                  store=True,
                                  readonly=True,
                                  default=0)
    # NOTE: PROJECT STATUS

    project_instruction = fields.Html('Project Instruction')
    project_status = fields.Selection(string='Project Status',
                                      selection=project_status_list,
                                      required=True,
                                      default='in progress')
    payment_status = fields.Selection(string='Payment Status',
                                      selection=payment_status_list,
                                      default='unpaid')

    po_details = fields.One2many("merctrans.pos",
                                 "project_id",
                                 string="Purchase Orders in this Project")

    def _get_client_name(self):
        self.client_name = ''
        for record in self:
            if record.client:
                record.client_name += record.client.name
            else:
                record.client_name = 'default bug'

    @api.model
    def create(self, vals):
        print("Project Create Vals ", vals)
        vals['number_id'] = self.env['ir.sequence'].next_by_code(
            'merctrans.project') or _('New')
        return super(MercTransProjects, self).create(vals)

    # @api.model
    # @api.model # đoạn code bên dưới gây bug khi chỉnh sửa project
    # def write(self, vals):
    #     print("Project Write Vals ", vals)
    #     return super(MercTransProjects, self).write(vals)

    # Auto genarate porject_id with client name, datetime and native id

    @api.onchange('client')
    @api.depends('client')
    def _get_project_id(self):
        create_time = datetime.today().strftime('%Y%m%d')
        for project in self:
            if project.client:
                # client is many2many nen can chinh sua lai 1 chut, chi lay ten cua thang dau tien, should be change with project.client
                client_name = project.client[0].name if len(
                    project.client) > 1 else project.client.name
                short_name = client_name[:4].upper()
                project.project_id = f"{short_name}-{create_time}-{project.number_id}"
            else:
                project.project_id = "on change"

    @api.onchange('volume', 'rate_per_work_unit')
    @api.depends('volume', 'sale_rate', 'discount')
    def _compute_project_value(self):
        for project in self:
            project.project_value = (
                100 -
                project.discount) / 100 * project.volume * project.sale_rate

    @api.constrains('start_date', 'due_date')
    def date_constrains(self):
        for project in self:
            if project.due_date < project.start_date:
                raise ValidationError(
                    'Due date must be greater than Start date!')

    @api.depends('po_details')
    def _compute_po_value(self):
        for job in self:
            job.total_po_value = sum(po.po_value for po in job.po_details)

    @api.onchange('project_value', 'total_po_value')
    @api.depends('project_value', 'total_po_value')
    def _compute_margin(self):
        for project in self:
            if project.project_value > 0:
                project.project_margin = (project.project_value - project.total_po_value) / project.project_value



class MercTransInvoices(models.Model):
    _name = 'merctrans.invoices'
    _rec_name = 'invoice_name'
    _description = 'MercTrans Invoices for Project Managers'

    status_list = [('invoiced', 'Invoiced'), ('paid', 'Paid'),
                   ('unpaid', 'Unpaid')]

    invoice_id = fields.Integer('Invoice ID')
    invoice_name = fields.Char('Invoice name')
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
                                      selection=status_list, default='Unpaid')

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


