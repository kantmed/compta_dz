from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CaActivityCategory(models.Model):
    _name = "ca.activity.category"
    _description = "Activity Category"
    _order = "sequence, name"
    _inherit = ["ca.audit.mixin"]

    code = fields.Char(required=True)
    name = fields.Char(required=True, translate=True)
    name_ar = fields.Char(string="Arabic Name")
    name_en = fields.Char(string="English Name")
    description = fields.Text()
    parent_id = fields.Many2one("ca.activity.category", string="Parent Category", ondelete="restrict", index=True)
    child_ids = fields.One2many("ca.activity.category", "parent_id", string="Child Categories")
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    _code_uniq = models.Constraint("unique(code)", "The activity category code must be unique.")

    @api.constrains("parent_id")
    def _check_parent(self):
        for record in self:
            if record.parent_id and record.parent_id == record:
                raise ValidationError(_("A category cannot be its own parent."))
            if record.parent_id:
                parent = record.parent_id
                while parent:
                    if parent == record:
                        raise ValidationError(_("Recursive category hierarchy is not allowed."))
                    parent = parent.parent_id
