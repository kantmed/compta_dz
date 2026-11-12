from odoo import models


class AccountPayment(models.Model):
    _inherit = ["account.payment", "ca.audit.mixin"]
