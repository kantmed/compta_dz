from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CaCollaborationDocumentRequest(models.Model):
    _name = "ca.collaboration.document.request"
    _description = "Collaboration Document Request"
    _order = "date_request desc, id desc"
    _inherit = ["ca.audit.mixin"]

    name = fields.Char(required=True)
    reference = fields.Char(required=True, copy=False, default="New", readonly=True)
    description = fields.Text()
    collaboration_id = fields.Many2one("ca.collaboration", required=True, ondelete="cascade", index=True)
    mandate_id = fields.Many2one("ca.mandate", related="collaboration_id.mandate_id", store=True, readonly=True)
    company_id = fields.Many2one("res.company", related="collaboration_id.company_id", store=True, readonly=True)
    folder_id = fields.Many2one("ca.accounting.folder", related="collaboration_id.folder_id", store=True, readonly=True)
    requester_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user)
    recipient_id = fields.Many2one("res.users", required=True)
    date_request = fields.Date(default=fields.Date.today, required=True)
    date_due = fields.Date()
    date_response = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("in_progress", "In progress"),
            ("received", "Documents received"),
            ("validated", "Validated"),
            ("refused", "Refused"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
    )
    requested_description = fields.Text(string="Requested Documents")
    transmitted_document_ids = fields.Many2many(
        "ir.attachment",
        "ca_collaboration_document_request_attachment_rel",
        "request_id",
        "attachment_id",
        string="Transmitted Documents",
    )
    comment = fields.Text()

    _ALLOWED_TRANSITIONS = {
        "draft": {"sent", "cancelled"},
        "sent": {"in_progress", "received", "cancelled"},
        "in_progress": {"received", "cancelled"},
        "received": {"validated", "refused", "cancelled"},
        "validated": set(),
        "refused": {"sent", "cancelled"},
        "cancelled": set(),
    }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = self.env["ir.sequence"].next_by_code("ca.collaboration.document.request") or "New"
            if vals.get("state") not in (None, False, "draft"):
                raise ValidationError(_("A new document request must start in draft status."))
            vals["state"] = vals.get("state") or "draft"
        return super().create(vals_list)

    @api.constrains("collaboration_id")
    def _check_collaboration_active(self):
        for request in self:
            if request.collaboration_id.state != "active" or request.collaboration_id.mandate_id.state != "active":
                raise ValidationError(_("Document requests can only be created for an active collaboration with an active mandate."))

    @api.constrains("recipient_id", "collaboration_id")
    def _check_recipient(self):
        for request in self:
            member = request.collaboration_id.member_ids.filtered(lambda m: m.user_id == request.recipient_id and m.is_effectively_active())
            if not member:
                raise ValidationError(_("The recipient must be an active member of the collaboration."))

    @api.constrains("date_request", "date_due", "date_response")
    def _check_dates(self):
        for request in self:
            if request.date_due and request.date_due < request.date_request:
                raise ValidationError(_("The due date cannot be earlier than the request date."))
            if request.date_response and request.date_response < request.date_request:
                raise ValidationError(_("The response date cannot be earlier than the request date."))

    def _check_transition(self, new_state):
        for request in self:
            if new_state not in self._ALLOWED_TRANSITIONS.get(request.state, set()):
                raise ValidationError(_("This status transition is not allowed."))

    def action_send(self):
        self._check_transition("sent")
        self.state = "sent"

    def action_start(self):
        self._check_transition("in_progress")
        self.state = "in_progress"

    def action_receive(self):
        self._check_transition("received")
        self.date_response = fields.Date.today()
        self.state = "received"

    def action_validate(self):
        self._check_transition("validated")
        self.state = "validated"

    def action_refuse(self):
        self._check_transition("refused")
        self.state = "refused"

    def action_cancel(self):
        self._check_transition("cancelled")
        self.state = "cancelled"

    def write(self, vals):
        if "state" in vals:
            self._check_transition(vals["state"])
        return super().write(vals)
