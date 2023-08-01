from odoo import models, api, fields, _


class OtManagement(models.Model):
    _name = "ot.management"
    _description = 'OT Management'

    project_id = fields.Many2one('project.project', string='Project', required=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', required=True)
    ot_month = fields.Char(string='OT Month', compute='_compute_ot_month', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True, default=lambda self: self.employee_default())
    dl_manager_id = fields.Many2one('hr.employee', string='Department lead', readonly=True, default=lambda self: self.employee_default_dl())
    create_date = fields.Datetime('Create Date', readonly=True)
    additional_hours = fields.Float('OT hours', compute='_compute_additional_hours', digits=(12, 0), default='0', store=True)
    ot_lines = fields.One2many('ot.registration.lines', 'ot_ids', string='OT Lines')
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

    @api.depends('ot_lines.date_from', 'ot_lines.date_to')
    def _compute_additional_hours(self):
        for rec in self:
            for line in rec.ot_lines:
                date_from = line.date_from.date()
                date_to = line.date_to.date()
                hour_from = line.date_from.hour
                hour_to = line.date_to.hour
                total = date_to - date_from
                hour1 = total.days * 24 + (hour_to - hour_from)
                rec.additional_hours = hour1