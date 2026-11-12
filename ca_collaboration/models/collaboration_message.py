from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CaCollaborationMessage(models.Model):
    _name = "ca.collaboration.message"
    _description = "Collaboration Message"
    _order = "date desc, id desc"
    _inherit = ["ca.audit.mixin"]

    collaboration_id = fields.Many2one("ca.collaboration", required=True, ondelete="cascade", index=True)
    task_id = fields.Many2one("ca.collaboration.task", ondelete="set null", index=True)
    request_id = fields.Many2one("ca.collaboration.document.request", ondelete="set null", index=True)
    author_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user, index=True)
    recipient_ids = fields.Many2many("res.users", "ca_collaboration_message_recipient_rel", "message_id", "user_id", string="Recipients")
    body = fields.Text(required=True)
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "ca_collaboration_message_attachment_rel",
        "message_id",
        "attachment_id",
        string="Attachments",
    )
    message_type = fields.Selection(
        [("comment", "Comment"), ("question", "Question"), ("answer", "Answer"), ("system", "System")],
        default="comment",
        required=True,
    )
    is_read = fields.Boolean(default=False)
    read_date = fields.Datetime()

    @api.constrains("collaboration_id")
    def _check_collaboration_active(self):
        for message in self:
            if message.collaboration_id.state != "active" or message.collaboration_id.mandate_id.state != "active":
                raise ValidationError(_("Messages can only be created for an active collaboration with an active mandate."))

    @api.constrains("author_id", "collaboration_id")
    def _check_author(self):
        for message in self:
            member = message.collaboration_id.member_ids.filtered(lambda m: m.user_id == message.author_id and m.is_effectively_active())
            if not member:
                raise ValidationError(_("The author must be an active member of the collaboration."))

    @api.constrains("recipient_ids", "collaboration_id")
    def _check_recipients(self):
        for message in self:
            for recipient in message.recipient_ids:
                member = message.collaboration_id.member_ids.filtered(lambda m: m.user_id == recipient and m.is_effectively_active())
                if not member:
                    raise ValidationError(_("All recipients must be active members of the collaboration."))

    def action_mark_read(self):
        self.write({"is_read": True, "read_date": fields.Datetime.now()})
