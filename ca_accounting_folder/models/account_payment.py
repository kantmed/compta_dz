from odoo import fields, models


from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    ca_accounting_folder_id = fields.Many2one(
        "ca.accounting.folder",
        string="Accounting Folder",
        related="move_id.ca_accounting_folder_id",
        store=True,
        readonly=True,
        index=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        payments = super().create(vals_list)
        for payment in payments:
            if payment.move_id and not payment.move_id.ca_accounting_folder_id:
                folder = False
                if payment.invoice_ids:
                    folder = payment.invoice_ids[:1].ca_accounting_folder_id
                if folder:
                    payment.move_id.ca_accounting_folder_id = folder
        return payments


    def action_post(self):
        res = super().action_post()
        for payment in self:
            if payment.move_id and not payment.move_id.ca_accounting_folder_id:
                folder = False
                if payment.reconciled_invoice_ids:
                    folder = payment.reconciled_invoice_ids[:1].ca_accounting_folder_id
                elif payment.invoice_ids:
                    folder = payment.invoice_ids[:1].ca_accounting_folder_id
                if folder:
                    payment.move_id.ca_accounting_folder_id = folder
        return res
