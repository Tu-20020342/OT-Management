from odoo import models, fields, api


class OTRequest(models.Model):
    _name = 'ot.request'
    _description = 'OT Request'

    project = fields.Many2one('project.project', string='Project', required=True)
    employee = fields.Many2one('hr.employee', string='Employee')
    manager_approve = fields.Many2one('hr.employee', string='Manager Approve', required=True)
    ot_hours = fields.Float(string='OT Hours', default=0)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('to_approve', 'To Approve'),
        ('pm_approved', 'PM Aproved'),
        ('dl_approved', 'DL Approved'),
        ('refused', 'Refused')
    ], string='Status', required=True, copy=False,
        tracking=True, default='draft')
    ot_month = fields.Date(string='OT Month')
    create_date = fields.Date(string='Create date')
    department_lead = fields.Many2one('hr.employee', string='Department Lead')
    ot_total = fields.Float(string='Total OT')

    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    ot_category = fields.Char(string='OT Category')
    wfh = fields.Boolean(string='WFH')
    job_taken = fields.Char(string='Job Taken')
    late_approved = fields.Date(string='Late Approved')
    hr_notes = fields.Text(string='HR Notes')
    attendance_notes = fields.Text(string='Attendance Notes')
    warning = fields.Char(string='Warning', default='Exceed OT plan')

