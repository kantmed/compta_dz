from odoo import models


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _reconcile_payments(self, to_process, edit_mode=False):
        result = super()._reconcile_payments(to_process, edit_mode=edit_mode)
        for vals in to_process:
            payment = vals.get("payment")
            if payment and payment.move_id and not payment.move_id.ca_accounting_folder_id:
                folder = False
                if payment.reconciled_invoice_ids:
                    folder = payment.reconciled_invoice_ids[:1].ca_accounting_folder_id
                elif payment.invoice_ids:
                    folder = payment.invoice_ids[:1].ca_accounting_folder_id
                if folder:
                    payment.move_id.with_context(ca_allow_folder_change=True).ca_accounting_folder_id = folder
        return result
