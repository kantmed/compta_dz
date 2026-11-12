from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    ca_accounting_folder_id = fields.Many2one(
        "ca.accounting.folder",
        string="Accounting Folder",
        index=True,
        ondelete="restrict",
    )

    @api.constrains("ca_accounting_folder_id", "company_id")
    def _check_ca_accounting_folder_company(self):
        for move in self:
            if move.ca_accounting_folder_id and move.ca_accounting_folder_id.company_id != move.company_id:
                raise ValidationError(_("The accounting folder must belong to the same company as the move."))

    def _check_folder_change_allowed(self):
        for move in self:
            if move.state == "posted" and not self.env.context.get("ca_allow_folder_change"):
                raise ValidationError(_("The accounting folder cannot be changed after posting."))

    def write(self, vals):
        if "ca_accounting_folder_id" in vals:
            self._check_folder_change_allowed()
        return super().write(vals)
