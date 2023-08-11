from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError


class OtManagement(models.Model):
    _name = "ot.management"
    _description = 'OT Management'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', required=True)
    ot_month = fields.Char(string='OT Month', compute='_compute_ot_month', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True,
                                  default=lambda self: self.get_employee())
    dl_manager_id = fields.Many2one('hr.employee', string='Department lead',
                                    default=lambda self: self.employee_default_dl(), readonly=True)
    create_date = fields.Datetime('Create Date', readonly=True)
    additional_hours = fields.Float('OT hours', related='ot_lines.additional_hours', digits=(12, 0), default='0',
                                    store=True)
    total_ot = fields.Float('Total OT', compute='_compute_total_ot', default='0', store=True)
    ot_lines = fields.One2many('ot.registration.lines', 'ot_management_id', string='OT Lines')
    state = fields.Selection([('draft', 'Draft'),
                              ('to_approve', 'To Approve'),
                              ('approved', 'PM Approved'),
                              ('done', 'DL Approved'),
                              ('refused', 'Refused')], string='State', default='draft', readonly=True)

    @api.depends('ot_lines.date_from')
    def _compute_ot_month(self):
        for rec in self:
            for line in rec.ot_lines:
                rec.ot_month = line.date_from.date().strftime('%m/%Y')

    @api.depends('additional_hours')
    def _compute_total_ot(self):
        for rec in self:
            for line in rec.ot_lines:
                if line:
                    rec.total_ot += line.additional_hours
                else:
                    rec.total = 0

    def get_employee(self):
        print('whyy?')
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self._uid)], limit=1)
        return employee

    @api.onchange('project_id')
    def management_pm(self):
        employees = self.env['hr.employee'].sudo().search([])
        for employee in employees:
            if self.project_id.user_id == employee.user_id:
                self.manager_id = employee.id

    def draft_request(self):
        for rec in self:
            rec.state = 'draft'

    def employee_default_dl(self):
        return self.env.ref('ot_management.hr_employee_dl_data').id

    @api.constrains('ot_lines')
    def check_create(self):
        for rec in self:
            if not rec.ot_lines:
                raise ValidationError('Bạn chưa nhập OT, vui lòng nhập lại!!!')

    def action_submit(self):
        for rec in self:
            rec.state = 'to_approve'
            template = self.env.ref('ot_management.new_request_to_pm_template')
            template.send_mail(rec.id, force_send=True)

        return True

    @api.multi
    def send_ot_request_email(self):
        template = self.env.ref('ot_management.new_request_to_pm_template')
        for rec in self:
            self.env['mail.template'].browse(template.id).send_mail(rec.id)

    def get_link_record(self):
        for rec in self:
            return '/web#model=ot.management&id=%s&view_type=form' % rec.id
