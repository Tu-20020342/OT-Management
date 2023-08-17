from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError


class OtManagement(models.Model):
    _name = "ot.management"
    _description = 'OT Management'

    name = fields.Char('Name', related='employee_id.name', store=True)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', required=True)
    ot_month = fields.Char(string='OT Month', compute='_compute_ot_month', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True,
                                  default=lambda self: self.get_employee())
    dl_manager_id = fields.Many2one('hr.employee', string='Department lead',
                                    default=lambda self: self.get_default_dl(), readonly=True)
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

    @api.constrains('ot_lines', 'additional_hours')
    def check_create(self):
        for rec in self:
            if not rec.ot_lines:
                raise ValidationError('Bạn chưa nhập OT, vui lòng nhập lại!!!')
            elif rec.additional_hours == 0:
                raise ValidationError('Thời gian OT không hợp lệ, vui lòng nhập lại!!!')

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
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        return employee.id if employee else False

    @api.onchange('project_id')
    def management_pm(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.project_id.user_id.id)], limit=1)
        if employee:
            self.manager_id = employee.id
        else:
            self.manager_id = False

    def get_default_dl(self):
        return self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1).parent_id

    def action_submit(self):
        for rec in self:
            rec.state = 'to_approve'
            mail_template = self.env.ref('ot_management.new_request_to_pm_template')
            mail_template.send_mail(self.id, force_send=True)

            # if rec.env.user.has_group('ot_management.ot_management_group_dl'):
            #     rec.state = 'approved'
            #     rec.send_mail('new_request_to_dl_template')
            # elif rec.env.user.has_group('ot_management.ot_management_group_pm'):
            #     rec.state = 'approved'
            #     self.send_mail('new_request_to_dl_template')
            # elif rec.env.user.has_group('ot_management.ot_management_group_user'):
            #     rec.state = 'to_approve'
            #     rec.send_mail('new_request_to_pm_template')

    @api.multi
    def send_ot_request_email(self, email_template):
        template = self.env.ref('ot_management.' + email_template)
        for rec in self:
            self.env['mail.template'].browse(template.id).send_mail(rec.id)

    def get_link_record(self):
        for rec in self:
            return '/web#model=ot.management&id=%s&view_type=form' % rec.id

    def button_pm_approve(self):
        for record in self:
            if record.env.user.has_group('ot_management.ot_management_group_pm') and record.state == 'to_approve':
                record.state = 'approved'
                mail_template = self.env.ref('ot_management.new_request_to_pm_template')
                mail_template.send_mail(self.id, force_send=True)

    def button_dl_approve(self):
        for record in self:
            if record.env.user.has_group('ot_management.ot_management_group_dl'):
                record.state = 'done'
                mail_template = self.env.ref('ot_management.new_request_to_dl_template')
                mail_template.send_mail(self.id, force_send=True)

    def refuse_request(self):
        for record in self:
            if self.env.user.has_group('ot_management.ot_management_group_dl') and \
                    self.state not in ['draft', 'done']:
                self.state = 'refused'
                self.send_ot_request_email('dl_refuse_request_template')
            elif self.env.user.has_group('ot_management.ot_management_group_pm') and \
                    self.state not in ['draft', 'done']:
                self.state = 'refused'
                self.send_ot_request_email('pm_refuse_request_template')

    def draft_request(self):
        for record in self:
            if record.state == 'refused':
                record.state = 'draft'
