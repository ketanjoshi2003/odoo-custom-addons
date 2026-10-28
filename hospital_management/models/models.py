from odoo import models, fields

class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient Record'

    name = fields.Char(string='Patient Name', required=True)
    age = fields.Integer(string='Age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', default='male')
    notes = fields.Text(string='Medical Notes')
