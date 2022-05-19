# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


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


class MercTransProjects(models.Model):
    _name = 'merctrans.projects'
    _description = 'MercTrans Projects'
    _rec_name = 'job_name'

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

    job_id = fields.Integer('Project ID')
    job_name = fields.Char('Project Name', default='Project Name')
    client = fields.Many2many('res.partner', string='Clients', required=True)

    # services contain tags
    services_ids = fields.Many2many('merctrans.services', string='Services')
    job_instruction = fields.Char('Project Instruction')
    source_language = fields.Selection(string="Source Languages",
                                       selection=language_list,
                                       default="Select a language")
    target_language = fields.Selection(string="Target Language",
                                       selection=language_list,
                                       default="Select a language")
    discount = fields.Integer('Discount (%)')
    # add discount field
    # fixed job

    work_unit = fields.Selection(string='Work Unit', selection=work_unit_list)
    volume = fields.Integer('Project Volume')
    currency_id = fields.Many2one('res.currency', string='Currency')
    sale_rate_per_work_unit = fields.Float('Sale rate per Work Unit')
    # production_rate_per_work_unit = fields.Float('Production rate per Work Unit')
    job_value = fields.Monetary("Job Value",
                                compute="_compute_job_value",
                                currency_field='currency_id',
                                store=True,
                                readonly=True)

    project_manager = fields.Many2one('res.users', string='Project Manager')
    start_date = fields.Date(string='Start Date')
    due_date = fields.Date(string='Due Date')
    project_status = fields.Selection(string='Project Status',
                                      selection=project_status_list)
    payment_status = fields.Selection(string='Payment Status',
                                      selection=payment_status_list)

    @api.model
    def create(self, vals):
        print("Project Create Vals ", vals)
        return super(MercTransProjects, self).create(vals)

    def write(self, vals):
        print("Project Write Vals ", vals)
        return super(MercTransProjects, self).write(vals)

    @api.onchange('volume', 'rate_per_work_unit')
    @api.depends('volume', 'sale_rate_per_work_unit', 'discount')
    def _compute_job_value(self):
        for project in self:
            project.job_value = (
                100 - project.discount
            ) / 100 * project.volume * project.sale_rate_per_work_unit

    @api.constrains('start_date', 'due_date')
    def date_constrains(self):
        for project in self:
            if project.due_date < project.start_date:
                raise ValidationError(
                    'Due date must be greater than Start date!')


class MercTransInvoices(models.Model):
    _name = 'merctrans.invoices'
    _rec_name = 'invoice_name'
    _description = 'MercTrans Invoices for Project Managers'

    status_list = [('invoiced', 'Invoiced'), ('paid', 'Paid'),
                   ('unpaid', 'Unpaid')]

    invoice_id = fields.Integer('Invoice ID')
    invoice_name = fields.Char('Invoice name')
    invoice_date = fields.Date(string='Invoice Date')
    invoice_client = fields.Many2one('res.partner',
                                     string='Client',
                                     required='True')
    invoice_details_ids = fields.Many2many('merctrans.projects',
                                           string='Invoice Lines')
    currency_id = fields.Many2one('res.currency', string='Currency')
    invoice_value = fields.Monetary("Invoice Value",
                                    compute="_compute_invoice_value",
                                    currency_field='currency_id')
    # invoice_details_ids = fields.Many2many('merctrans.invoices.lines', 'job_id', string="Invoice Lines")
    invoice_status = fields.Selection(string="Invoice Status",
                                      selection=status_list)

    @api.depends('invoice_details_ids')
    def _compute_invoice_value(self):
        for item in self:
            item.invoice_value = sum(x.job_value
                                     for x in item.invoice_details_ids)

    @api.constrains('invoice_details_ids')
    def currency_constrains(self):
        for job in self:
            for x in job.invoice_details_ids:
                if job.currency_id != x.currency_id:
                    raise ValidationError(
                        'Job currency must be the same as invoice currency!')

    @api.model
    def create(self, vals):
        print("Invoices Create Vals ", vals)
        return super(MercTransInvoices, self).create(vals)

    def write(self, vals):
        print("Invoices Write Vals ", vals)
        return super(MercTransInvoices, self).write(vals)

    @api.onchange('invoice_status')
    def sync_status(self):
        
        for project in self.invoice_details_ids:
            if self.invoice_status == 'paid':
                project.write({'payment_status': 'paid'})
            if self.invoice_status == 'invoiced':
                project.write({'payment_status': 'invoiced'})
