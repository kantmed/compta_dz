from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CaMandateMission(models.Model):
    _name = "ca.mandate.mission"
    _description = "Mandate Mission"
    _order = "sequence, name"
    _inherit = ["ca.audit.mixin"]

    code = fields.Char(required=True)
    name = fields.Char(required=True, translate=True)
    name_ar = fields.Char(string="Arabic Name")
    name_en = fields.Char(string="English Name")
    description = fields.Text()
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    _code_uniq = models.Constraint("unique(code)", "The mission code must be unique.")

    @api.constrains("code")
    def _check_code(self):
        for mission in self:
            if not mission.code:
                raise ValidationError(_("The code is required."))
