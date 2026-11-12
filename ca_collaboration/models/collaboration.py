from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CaCollaboration(models.Model):
    _name = "ca.collaboration"
    _description = "Collaboration"
    _order = "date_start desc, id desc"
    _inherit = ["ca.audit.mixin"]

    name = fields.Char(required=True)
    reference = fields.Char(required=True, copy=False, default="New", readonly=True)
    company_id = fields.Many2one("res.company", string="Client Company", required=True, index=True)
    firm_id = fields.Many2one("res.company", string="Accounting Firm", required=True, index=True)
    mandate_id = fields.Many2one("ca.mandate", string="Mandate", required=True, index=True)
    folder_id = fields.Many2one("ca.accounting.folder", string="Accounting Folder", index=True)
    client_manager_id = fields.Many2one("res.partner", string="Client Manager")
    firm_manager_id = fields.Many2one("res.users", string="Firm Manager", required=True, default=lambda self: self.env.user)
    date_start = fields.Date()
    date_end = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
    )
    description = fields.Text()
    member_ids = fields.One2many("ca.collaboration.member", "collaboration_id", string="Members")
    authorized_member_ids = fields.Many2many("res.users", "ca_collaboration_authorized_member_rel", "collaboration_id", "user_id", compute="_compute_authorized_member_ids", store=True, readonly=True)
    task_ids = fields.One2many("ca.collaboration.task", "collaboration_id", string="Tasks")
    request_ids = fields.One2many("ca.collaboration.document.request", "collaboration_id", string="Document Requests")
    message_ids = fields.One2many("ca.collaboration.message", "collaboration_id", string="Messages")
    open_task_count = fields.Integer(compute="_compute_counts", store=False)
    pending_request_count = fields.Integer(compute="_compute_counts", store=False)

    _ALLOWED_TRANSITIONS = {
        "draft": {"pending", "cancelled"},
        "pending": {"active", "cancelled"},
        "active": {"suspended", "done", "cancelled"},
        "suspended": {"active", "cancelled"},
        "done": set(),
        "cancelled": set(),
    }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = self.env["ir.sequence"].next_by_code("ca.collaboration") or "New"
            if vals.get("state") not in (None, False, "draft"):
                raise ValidationError(_("A new collaboration must start in draft status."))
            vals["state"] = "draft"
        records = super().create(vals_list)
        return records

    @api.depends("member_ids.user_id", "member_ids.active", "member_ids.date_start", "member_ids.date_end")
    def _compute_authorized_member_ids(self):
        for collaboration in self:
            today = fields.Date.today()
            users = collaboration.member_ids.filtered(
                lambda member: member.is_effectively_active()
                and (not member.date_start or member.date_start <= today)
                and (not member.date_end or member.date_end >= today)
            ).user_id
            collaboration.authorized_member_ids = users

    @api.depends("task_ids.state", "request_ids.state")
    def _compute_counts(self):
        for collaboration in self:
            collaboration.open_task_count = len(collaboration.task_ids.filtered(lambda t: t.state not in ("done", "cancelled")))
            collaboration.pending_request_count = len(collaboration.request_ids.filtered(lambda r: r.state in ("sent", "in_progress")))

    @api.constrains("company_id", "firm_id")
    def _check_companies(self):
        for collaboration in self:
            if collaboration.company_id and collaboration.firm_id and collaboration.company_id == collaboration.firm_id:
                raise ValidationError(_("The client company and the accounting firm must be different."))

    @api.constrains("mandate_id", "company_id", "firm_id", "folder_id")
    def _check_mandate(self):
        for collaboration in self:
            mandate = collaboration.mandate_id
            if mandate and mandate.company_id != collaboration.company_id:
                raise ValidationError(_("The mandate must belong to the client company."))
            if mandate and mandate.firm_id != collaboration.firm_id:
                raise ValidationError(_("The mandate must belong to the accounting firm."))
            if collaboration.folder_id and collaboration.folder_id.company_id != collaboration.company_id:
                raise ValidationError(_("The folder must belong to the client company."))
            if collaboration.mandate_id.state != "active":
                raise ValidationError(_("The mandate must be active."))
            if collaboration.state in ("pending", "active") and collaboration.mandate_id.state != "active":
                raise ValidationError(_("The mandate must be active for an operational collaboration."))

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for collaboration in self:
            if collaboration.date_start and collaboration.date_end and collaboration.date_end < collaboration.date_start:
                raise ValidationError(_("The end date cannot be earlier than the start date."))

    def _check_transition(self, new_state):
        for collaboration in self:
            if new_state not in self._ALLOWED_TRANSITIONS.get(collaboration.state, set()):
                raise ValidationError(_("This status transition is not allowed."))

    def action_submit(self):
        self._check_transition("pending")
        self.state = "pending"

    def action_activate(self):
        self._check_transition("active")
        self.state = "active"
        self._ca_notify("Collaboration activated")

    def action_suspend(self):
        self._check_transition("suspended")
        self.state = "suspended"

    def action_resume(self):
        self._check_transition("active")
        self.state = "active"

    def action_done(self):
        self._check_transition("done")
        self.state = "done"

    def action_cancel(self):
        self._check_transition("cancelled")
        self.state = "cancelled"

    def write(self, vals):
        if "state" in vals:
            self._check_transition(vals["state"])
        return super().write(vals)

    def _ca_notify(self, body):
        for collaboration in self:
            author = collaboration.firm_manager_id
            member = collaboration.member_ids.filtered(lambda m: m.user_id == author and m.is_effectively_active()) if author else False
            if not member and collaboration.member_ids:
                author = collaboration.member_ids.filtered(lambda m: m.is_effectively_active())[:1].user_id
            if not author:
                continue
            self.env["ca.collaboration.message"].sudo().create(
                {
                    "collaboration_id": collaboration.id,
                    "author_id": author.id,
                    "body": body,
                    "message_type": "system",
                }
            )

    def unlink(self):
        for collaboration in self:
            if collaboration.state in ("active", "pending"):
                raise ValidationError(_("An active or pending collaboration cannot be deleted."))
        return super().unlink()
