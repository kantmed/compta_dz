from odoo import models


class CaAccountingFolder(models.Model):
    _inherit = ["ca.accounting.folder", "ca.audit.mixin"]
