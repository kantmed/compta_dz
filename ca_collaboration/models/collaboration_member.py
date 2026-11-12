from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CaCollaborationMember(models.Model):
    _name = "ca.collaboration.member"
    _description = "Collaboration Member"
    _order = "collaboration_id, user_id"
    _inherit = ["ca.audit.mixin"]

    collaboration_id = fields.Many2one("ca.collaboration", required=True, ondelete="cascade", index=True)
    user_id = fields.Many2one("res.users", required=True, index=True)
    role = fields.Selection(
        [
            ("admin", "Administrator"),
            ("firm_manager", "Firm manager"),
            ("firm_collaborator", "Firm collaborator"),
            ("client_manager", "Client manager"),
            ("client_collaborator", "Client collaborator"),
            ("reader", "Reader"),
        ],
        default="reader",
        required=True,
    )
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)
    is_responsible = fields.Boolean(default=False)
    operational_permissions = fields.Text()

    @api.constrains("user_id", "role", "collaboration_id")
    def _check_member_company(self):
        for member in self:
            collab = member.collaboration_id
            if member.role and member.role.startswith("firm_"):
                if collab.firm_id not in member.user_id.company_ids:
                    raise ValidationError(_("The collaborator must belong to the accounting firm."))
            elif member.role and member.role.startswith("client_"):
                if collab.company_id not in member.user_id.company_ids:
                    raise ValidationError(_("The collaborator must belong to the client company."))

    @api.constrains("user_id", "collaboration_id")
    def _check_unique_member(self):
        for member in self:
            duplicates = self.search(
                [
                    ("id", "!=", member.id),
                    ("collaboration_id", "=", member.collaboration_id.id),
                    ("user_id", "=", member.user_id.id),
                    ("active", "=", True),
                ]
            )
            if duplicates:
                raise ValidationError(_("This user is already an active member of the collaboration."))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for member in self:
            if member.date_start and member.date_end and member.date_end < member.date_start:
                raise ValidationError(_("The end date cannot be earlier than the start date."))

    def is_effectively_active(self):
        self.ensure_one()
        today = fields.Date.today()
        if not self.active:
            return False
        if self.date_start and self.date_start > today:
            return False
        if self.date_end and self.date_end < today:
            return False
        return True
