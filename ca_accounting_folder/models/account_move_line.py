from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    ca_accounting_folder_id = fields.Many2one(
        "ca.accounting.folder",
        string="Accounting Folder",
        related="move_id.ca_accounting_folder_id",
        store=True,
        readonly=True,
        index=True,
    )
