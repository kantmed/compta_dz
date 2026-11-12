from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CaAccountingFolder(models.Model):
    _name = "ca.accounting.folder"
    _description = "Accounting Folder"
    _order = "company_id, name"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    manager_id = fields.Many2one(
        "res.users",
        required=True,
        default=lambda self: self.env.user,
        index=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("review", "In review"),
            ("closed", "Closed"),
            ("archived", "Archived"),
        ],
        default="draft",
        required=True,
    )
    description = fields.Text()
    collaborator_ids = fields.Many2many(
        "res.users",
        "ca_accounting_folder_collaborator_rel",
        "folder_id",
        "user_id",
        string="Collaborators",
    )
    opening_date = fields.Date()
    closing_date = fields.Date()

    _code_company_uniq = models.Constraint(
        "unique(code, company_id)",
        "The folder code must be unique within the company.",
    )

    _ALLOWED_TRANSITIONS = {
        "draft": {"active"},
        "active": {"review", "closed"},
        "review": {"active", "closed"},
        "closed": {"archived"},
        "archived": set(),
    }

    @api.constrains("company_id")
    def _check_company_required(self):
        for folder in self:
            if not folder.company_id:
                raise ValidationError(_("The company is required."))

    @api.constrains("manager_id")
    def _check_manager_required(self):
        for folder in self:
            if not folder.manager_id:
                raise ValidationError(_("The responsible user is required."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("company_id"):
                raise ValidationError(_("The company is required."))
            if not vals.get("manager_id"):
                raise ValidationError(_("The responsible user is required."))
            if vals.get("state") not in (None, False, "draft"):
                raise ValidationError(_("A new accounting folder must start in draft status."))
            vals["state"] = "draft"
        return super().create(vals_list)

    @api.constrains("manager_id", "company_id")
    def _check_manager_company(self):
        for folder in self:
            if folder.manager_id and folder.company_id not in folder.manager_id.company_ids:
                raise ValidationError(
                    _("The responsible user must have access to the selected company.")
                )

    @api.constrains("collaborator_ids", "company_id")
    def _check_collaborators_company(self):
        for folder in self:
            for user in folder.collaborator_ids:
                if folder.company_id not in user.company_ids:
                    raise ValidationError(
                        _("All collaborators must have access to the selected company.")
                    )

    @api.constrains("opening_date", "closing_date")
    def _check_dates(self):
        for folder in self:
            if (
                folder.opening_date
                and folder.closing_date
                and folder.closing_date < folder.opening_date
            ):
                raise ValidationError(
                    _("The closing date cannot be earlier than the opening date.")
                )

    @api.constrains("company_id")
    def _check_company_immutable(self):
        for folder in self:
            if folder._origin and folder.company_id != folder._origin.company_id:
                raise ValidationError(_("The company of an accounting folder cannot be changed."))

    def _check_transition(self, new_state):
        for folder in self:
            if new_state not in self._ALLOWED_TRANSITIONS.get(folder.state, set()):
                raise ValidationError(_("This status transition is not allowed."))
        if new_state == "closed":
            for folder in self:
                if (
                    folder.opening_date
                    and folder.closing_date
                    and folder.closing_date < folder.opening_date
                ):
                    raise ValidationError(
                        _("The closing date cannot be earlier than the opening date.")
                    )

    def action_activate(self):
        self._check_transition("active")
        self.state = "active"

    def action_review(self):
        self._check_transition("review")
        self.state = "review"

    def action_close(self):
        self._check_transition("closed")
        self.state = "closed"

    def action_archive(self):
        self._check_transition("archived")
        self.state = "archived"

    def write(self, vals):
        if "company_id" in vals:
            for folder in self:
                if vals.get("company_id") != folder.company_id.id:
                    raise ValidationError(_("The company of an accounting folder cannot be changed."))
        if "state" in vals:
            self._check_transition(vals["state"])
        if (
            any(folder.state == "archived" for folder in self)
            and not self.env.su
            and not self.env.user.has_group("ca_core.group_ca_core_admin")
        ):
            raise ValidationError(_("An archived accounting folder cannot be modified."))
        return super().write(vals)

    def unlink(self):
        if (
            any(folder.state == "archived" for folder in self)
            and not self.env.su
            and not self.env.user.has_group("ca_core.group_ca_core_admin")
        ):
            raise ValidationError(_("An archived accounting folder cannot be deleted."))
        return super().unlink()
