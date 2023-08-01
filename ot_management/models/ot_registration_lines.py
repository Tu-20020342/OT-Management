from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, time, timedelta
import pytz


class OtRegistrationLine(models.Model):
    _name = 'ot.registration.lines'
    _description = 'OT Registration detail'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    is_intern_contract = fields.Boolean('Is intern')
    project_id = fields.Many2one('project.project', string='Project')
    date_from = fields.Datetime('Form', default=datetime.today())
    date_to = fields.Datetime('To', default=datetime.today())
    category = fields.Selection([('normal_day', 'Ngày bình thường'),
                                 ('normal_day_morning', 'OT ban ngày (6h-8h30)'),
                                 ('normal_day_night', 'Ngày bình thường - Ban đêm'),
                                 ('saturday', 'thứ 7'),
                                 ('sunday', 'chủ nhật'),
                                 ('week_day_night', 'ngày cuối tuần - Ban đêm'),
                                 ('holiday', 'ngày lễ'),
                                 ('holiday_night', 'ngày lễ - ban đêm'),
                                 ('compensatory_normal', 'Bù ngày lễ vào ngày thường'),
                                 ('compensatory_night', 'Bù ngày lễ vào ban đêm'),
                                 ('unknown', 'không thể xác định')], string='Category')
    additional_hours = fields.Float('OT hours', compute='_compute_additional_hours', digits=(12, 0), default='0')
    job_taken = fields.Char('Job Taken', default='N/A')
    late_approved = fields.Boolean('Late approved', readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('to_approve', 'To Approve'),
                              ('approved', 'PM Approved'),
                              ('done', 'DL Approved'),
                              ('refused', 'Refused')], string='State', default='draft')
    is_wfh = fields.Boolean('WFH')
    ot_ids = fields.Many2one('ot.management', string='OT ID')
    notes = fields.Text('Note', readonly=True)
    attendance_notes = fields.Text('Attendance Notes', readonly=True)
    plan_hours = fields.Char('Warning', default='Exceed OT plan')

    def _compute_additional_hours(self):
        ots = self.env['ot.management'].sudo().search([])
        for rec in self:
            for ot in ots:
                if ot.employee_id.id == rec.employee_id.id:
                    rec.additional_hours = ot.additional_hours
