from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    ca_mandate_id = fields.Many2one(
        "ca.mandate",
        string="Accounting Mandate",
        compute="_compute_ca_mandate_id",
        store=True,
        index=True,
    )

    @api.depends("res_model", "res_id")
    def _compute_ca_mandate_id(self):
        for attachment in self:
            mandate = False
            if attachment.res_model == "ca.mandate" and attachment.res_id:
                mandate = self.env["ca.mandate"].browse(attachment.res_id).sudo()
            attachment.ca_mandate_id = mandate
