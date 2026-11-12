from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    ca_collaboration_id = fields.Many2one(
        "ca.collaboration",
        string="Collaboration",
        compute="_compute_ca_collaboration_id",
        store=True,
        index=True,
    )

    @api.depends("res_model", "res_id")
    def _compute_ca_collaboration_id(self):
        for attachment in self:
            collaboration = False
            if attachment.res_model == "ca.collaboration" and attachment.res_id:
                collaboration = self.env["ca.collaboration"].browse(attachment.res_id).sudo()
            elif attachment.res_model == "ca.collaboration.task" and attachment.res_id:
                task = self.env["ca.collaboration.task"].browse(attachment.res_id).sudo()
                collaboration = task.collaboration_id
            elif attachment.res_model == "ca.collaboration.document.request" and attachment.res_id:
                request = self.env["ca.collaboration.document.request"].browse(attachment.res_id).sudo()
                collaboration = request.collaboration_id
            elif attachment.res_model == "ca.collaboration.message" and attachment.res_id:
                message = self.env["ca.collaboration.message"].browse(attachment.res_id).sudo()
                collaboration = message.collaboration_id
            attachment.ca_collaboration_id = collaboration
