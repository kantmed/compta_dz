from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CaLegalForm(models.Model):
    _name = "ca.legal.form"
    _description = "Legal Form"
    _order = "sequence, name"
    _inherit = ["ca.audit.mixin"]

    code = fields.Char(required=True)
    name = fields.Char(required=True, translate=True)
    name_ar = fields.Char(string="Arabic Name")
    name_en = fields.Char(string="English Name")
    description = fields.Text()
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    regulatory_reference = fields.Char()
    validity_start = fields.Date()
    validity_end = fields.Date()

    _code_uniq = models.Constraint("unique(code)", "The legal form code must be unique.")

    @api.constrains("validity_start", "validity_end")
    def _check_validity_dates(self):
        for record in self:
            if record.validity_start and record.validity_end and record.validity_end < record.validity_start:
                raise ValidationError(_("The end date cannot be earlier than the start date."))

    @api.constrains("code")
    def _check_code(self):
        for record in self:
            if not record.code:
                raise ValidationError(_("The code is required."))
