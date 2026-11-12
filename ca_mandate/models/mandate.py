from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CaMandate(models.Model):
    _name = "ca.mandate"
    _description = "Accounting Mandate"
    _order = "date_start desc, id desc"
    _inherit = ["ca.audit.mixin"]

    name = fields.Char(required=True)
    reference = fields.Char(required=True, copy=False, default="New", readonly=True)
    company_id = fields.Many2one("res.company", string="Client Company", required=True, index=True)
    firm_id = fields.Many2one("res.company", string="Accounting Firm", required=True, index=True)
    date_signature = fields.Date()
    date_start = fields.Date(required=True)
    date_end = fields.Date()
    date_end_effective = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending validation"),
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
    )
    is_primary = fields.Boolean(default=True)
    mission_ids = fields.Many2many(
        "ca.mandate.mission",
        "ca_mandate_mission_rel",
        "mandate_id",
        "mission_id",
        string="Missions",
    )
    folder_ids = fields.Many2many(
        "ca.accounting.folder",
        "ca_mandate_folder_rel",
        "mandate_id",
        "folder_id",
        string="Covered Folders",
        domain="[('company_id', '=', company_id)]",
    )
    manager_id = fields.Many2one("res.users", string="Firm Manager", required=True, default=lambda self: self.env.user)
    client_manager_id = fields.Many2one("res.partner", string="Client Manager")
    collaborator_ids = fields.One2many("ca.mandate.collaborator", "mandate_id", string="Collaborators")
    document_ids = fields.Many2many(
        "ir.attachment",
        "ca_mandate_document_rel",
        "mandate_id",
        "attachment_id",
        string="Contract Documents",
    )
    previous_mandate_id = fields.Many2one("ca.mandate", string="Previous Mandate")
    successor_mandate_id = fields.Many2one("ca.mandate", string="Successor Mandate")
    notes = fields.Text()
    suspension_reason = fields.Text()
    termination_reason = fields.Text()

    _ALLOWED_TRANSITIONS = {
        "draft": {"pending"},
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
                vals["reference"] = self.env["ir.sequence"].next_by_code("ca.mandate") or "New"
            if vals.get("state") not in (None, False, "draft"):
                raise ValidationError(_("A new mandate must start in draft status."))
            vals["state"] = "draft"
        return super().create(vals_list)

    @api.constrains("company_id", "firm_id")
    def _check_companies(self):
        for mandate in self:
            if mandate.company_id and mandate.firm_id and mandate.company_id == mandate.firm_id:
                raise ValidationError(_("The client company and the accounting firm must be different."))

    @api.constrains("folder_ids", "company_id")
    def _check_folders(self):
        for mandate in self:
            for folder in mandate.folder_ids:
                if folder.company_id != mandate.company_id:
                    raise ValidationError(_("All covered folders must belong to the client company."))

    @api.constrains("date_start", "date_end", "date_end_effective")
    def _check_dates(self):
        for mandate in self:
            if mandate.date_start and mandate.date_end and mandate.date_end < mandate.date_start:
                raise ValidationError(_("The end date cannot be earlier than the start date."))
            if mandate.date_start and mandate.date_end_effective and mandate.date_end_effective < mandate.date_start:
                raise ValidationError(_("The effective end date cannot be earlier than the start date."))
            if mandate.date_end and mandate.date_end_effective and mandate.date_end_effective > mandate.date_end:
                raise ValidationError(_("The effective end date cannot be later than the planned end date."))

    @api.constrains("is_primary", "state", "company_id", "firm_id", "date_start", "date_end")
    def _check_primary_mandate(self):
        for mandate in self:
            if not mandate.is_primary:
                continue
            domain = [
                ("id", "!=", mandate.id),
                ("company_id", "=", mandate.company_id.id),
                ("is_primary", "=", True),
                ("state", "=", "active"),
            ]
            if mandate.date_start or mandate.date_end:
                domain.append(("date_start", "<=", mandate.date_end or mandate.date_start))
                domain.append(("date_end", ">=", mandate.date_start))
            conflicts = self.search(domain)
            if conflicts:
                raise ValidationError(_("An active primary mandate already exists for this company and period."))

    @api.constrains("previous_mandate_id", "successor_mandate_id", "company_id")
    def _check_mandate_links(self):
        for mandate in self:
            if mandate.previous_mandate_id and mandate.previous_mandate_id.company_id != mandate.company_id:
                raise ValidationError(_("The previous mandate must belong to the same client company."))
            if mandate.successor_mandate_id and mandate.successor_mandate_id.company_id != mandate.company_id:
                raise ValidationError(_("The successor mandate must belong to the same client company."))

    def _check_transition(self, new_state):
        for mandate in self:
            if new_state not in self._ALLOWED_TRANSITIONS.get(mandate.state, set()):
                raise ValidationError(_("This status transition is not allowed."))

    def action_submit(self):
        self._check_transition("pending")
        self.state = "pending"

    def action_validate(self):
        self._check_transition("active")
        self.state = "active"

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

    def unlink(self):
        for mandate in self:
            if mandate.state in ("active", "pending"):
                raise ValidationError(_("An active or pending mandate cannot be deleted."))
        return super().unlink()
