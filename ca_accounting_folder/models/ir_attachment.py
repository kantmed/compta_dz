from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    ca_accounting_folder_id = fields.Many2one(
        "ca.accounting.folder",
        string="Accounting Folder",
        compute="_compute_ca_accounting_folder_id",
        store=True,
        index=True,
    )

    @api.depends("res_model", "res_id")
    def _compute_ca_accounting_folder_id(self):
        for attachment in self:
            folder = False
            if attachment.res_model == "account.move" and attachment.res_id:
                move = self.env["account.move"].browse(attachment.res_id).sudo()
                folder = move.ca_accounting_folder_id
            attachment.ca_accounting_folder_id = folder
