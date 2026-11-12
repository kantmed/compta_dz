from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CaMandateCollaborator(models.Model):
    _name = "ca.mandate.collaborator"
    _description = "Mandate Collaborator"
    _order = "mandate_id, user_id"
    _inherit = ["ca.audit.mixin"]

    mandate_id = fields.Many2one("ca.mandate", required=True, ondelete="cascade", index=True)
    user_id = fields.Many2one("res.users", required=True, index=True)
    role = fields.Char()
    date_start = fields.Date()
    date_end = fields.Date()
    active = fields.Boolean(default=True)

    @api.constrains("user_id", "mandate_id")
    def _check_user_firm(self):
        for collaborator in self:
            if collaborator.mandate_id.firm_id and collaborator.user_id.company_id != collaborator.mandate_id.firm_id:
                # Allow users with explicit access to the firm; otherwise require firm company.
                if collaborator.mandate_id.firm_id not in collaborator.user_id.company_ids:
                    raise ValidationError(_("The collaborator must belong to the accounting firm."))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for collaborator in self:
            if collaborator.date_start and collaborator.date_end and collaborator.date_end < collaborator.date_start:
                raise ValidationError(_("The end date cannot be earlier than the start date."))
