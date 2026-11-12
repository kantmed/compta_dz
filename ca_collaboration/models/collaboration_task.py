from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CaCollaborationTask(models.Model):
    _name = "ca.collaboration.task"
    _description = "Collaboration Task"
    _order = "priority desc, date_deadline, id"
    _inherit = ["ca.audit.mixin"]

    name = fields.Char(required=True)
    reference = fields.Char(required=True, copy=False, default="New", readonly=True)
    description = fields.Text()
    collaboration_id = fields.Many2one("ca.collaboration", required=True, ondelete="cascade", index=True)
    mandate_id = fields.Many2one("ca.mandate", related="collaboration_id.mandate_id", store=True, readonly=True)
    folder_id = fields.Many2one("ca.accounting.folder", related="collaboration_id.folder_id", store=True, readonly=True)
    company_id = fields.Many2one("res.company", related="collaboration_id.company_id", store=True, readonly=True)
    assigned_to = fields.Many2one("res.users", index=True)
    created_by = fields.Many2one("res.users", default=lambda self: self.env.user, readonly=True)
    date_created = fields.Datetime(default=fields.Datetime.now, readonly=True)
    date_deadline = fields.Date()
    date_closed = fields.Datetime()
    priority = fields.Selection(
        [("low", "Low"), ("normal", "Normal"), ("high", "High"), ("urgent", "Urgent")],
        default="normal",
        required=True,
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("todo", "To do"),
            ("in_progress", "In progress"),
            ("waiting", "Waiting"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="new",
        required=True,
    )
    category = fields.Char()
    document_ids = fields.Many2many(
        "ir.attachment",
        "ca_collaboration_task_document_rel",
        "task_id",
        "attachment_id",
        string="Documents",
    )
    message_ids = fields.One2many("ca.collaboration.message", "task_id", string="Messages")

    _ALLOWED_TRANSITIONS = {
        "new": {"todo", "cancelled"},
        "todo": {"in_progress", "waiting", "cancelled"},
        "in_progress": {"waiting", "done", "cancelled"},
        "waiting": {"in_progress", "done", "cancelled"},
        "done": set(),
        "cancelled": set(),
    }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = self.env["ir.sequence"].next_by_code("ca.collaboration.task") or "New"
            if vals.get("state") not in (None, False, "new"):
                raise ValidationError(_("A new task must start in new status."))
            vals["state"] = vals.get("state") or "new"
        return super().create(vals_list)

    @api.constrains("collaboration_id")
    def _check_collaboration_active(self):
        for task in self:
            if task.collaboration_id.state != "active" or task.collaboration_id.mandate_id.state != "active":
                raise ValidationError(_("Tasks can only be created for an active collaboration with an active mandate."))

    @api.constrains("assigned_to", "collaboration_id")
    def _check_assignment(self):
        for task in self:
            if task.assigned_to:
                member = task.collaboration_id.member_ids.filtered(lambda m: m.user_id == task.assigned_to and m.is_effectively_active())
                if not member:
                    raise ValidationError(_("The assigned user must be an active member of the collaboration."))

    @api.constrains("date_deadline")
    def _check_deadline(self):
        return

    def _check_transition(self, new_state):
        for task in self:
            if new_state not in self._ALLOWED_TRANSITIONS.get(task.state, set()):
                raise ValidationError(_("This task status transition is not allowed."))

    def action_start(self):
        self._check_transition("in_progress")
        self.state = "in_progress"

    def action_wait(self):
        self._check_transition("waiting")
        self.state = "waiting"

    def action_done(self):
        self._check_transition("done")
        self.date_closed = fields.Datetime.now()
        self.state = "done"

    def action_cancel(self):
        self._check_transition("cancelled")
        self.state = "cancelled"

    def write(self, vals):
        if "state" in vals:
            self._check_transition(vals["state"])
        return super().write(vals)
