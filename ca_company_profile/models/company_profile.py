from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompanyProfile(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "ca.audit.mixin"]

    ca_legal_form_id = fields.Many2one("ca.legal.form", string="Legal Form")
    ca_trade_name = fields.Char(string="Trade Name")
    ca_incorporation_date = fields.Date(string="Incorporation Date")
    ca_activity_start_date = fields.Date(string="Activity Start Date")
    ca_share_capital = fields.Monetary(string="Share Capital", currency_field="currency_id")
    ca_company_duration = fields.Integer(string="Company Duration (years)")
    ca_legal_state = fields.Selection(
        [
            ("active", "In activity"),
            ("ceased", "Ceased"),
            ("liquidation", "In liquidation"),
            ("struck_off", "Struck off"),
        ],
        string="Legal State",
        default="active",
    )
    ca_legal_description = fields.Text(string="Legal Description")

    ca_nif = fields.Char(string="NIF")
    ca_nif_date = fields.Date(string="NIF Date")
    ca_nif_expiry = fields.Date(string="NIF Expiry Date")
    ca_nif_authority = fields.Char(string="NIF Issuing Authority")
    ca_nif_document_ids = fields.Many2many(
        "ir.attachment",
        "ca_company_profile_nif_attachment_rel",
        "company_id",
        "attachment_id",
        string="NIF Documents",
    )

    ca_nis = fields.Char(string="NIS")
    ca_nis_date = fields.Date(string="NIS Date")
    ca_nis_expiry = fields.Date(string="NIS Expiry Date")
    ca_nis_authority = fields.Char(string="NIS Issuing Authority")
    ca_nis_document_ids = fields.Many2many(
        "ir.attachment",
        "ca_company_profile_nis_attachment_rel",
        "company_id",
        "attachment_id",
        string="NIS Documents",
    )

    ca_rc = fields.Char(string="RC")
    ca_rc_date = fields.Date(string="RC Date")
    ca_rc_expiry = fields.Date(string="RC Expiry Date")
    ca_rc_authority = fields.Char(string="RC Issuing Authority")
    ca_rc_document_ids = fields.Many2many(
        "ir.attachment",
        "ca_company_profile_rc_attachment_rel",
        "company_id",
        "attachment_id",
        string="RC Documents",
    )

    ca_tax_article = fields.Char(string="Tax Article")
    ca_tax_article_date = fields.Date(string="Tax Article Date")
    ca_tax_article_expiry = fields.Date(string="Tax Article Expiry Date")
    ca_tax_article_authority = fields.Char(string="Tax Article Issuing Authority")

    ca_casnos_id = fields.Char(string="CASNOS ID")
    ca_casnos_date = fields.Date(string="CASNOS Date")
    ca_casnos_expiry = fields.Date(string="CASNOS Expiry Date")

    ca_cnas_id = fields.Char(string="CNAS ID")
    ca_cnas_date = fields.Date(string="CNAS Date")
    ca_cnas_expiry = fields.Date(string="CNAS Expiry Date")

    ca_approval_number = fields.Char(string="Approval Number")
    ca_approval_date = fields.Date(string="Approval Date")
    ca_approval_expiry = fields.Date(string="Approval Expiry Date")
    ca_approval_authority = fields.Char(string="Approval Issuing Authority")

    ca_tax_regime = fields.Char(string="Tax Regime")
    ca_vat_regime = fields.Char(string="VAT Regime")
    ca_vat_registered = fields.Boolean(string="VAT Registered")
    ca_vat_start_date = fields.Date(string="VAT Start Date")
    ca_vat_end_date = fields.Date(string="VAT End Date")
    ca_tax_office = fields.Char(string="Tax Office")
    ca_tax_inspection = fields.Char(string="Tax Inspection")
    ca_fiscal_notes = fields.Text(string="Fiscal Notes")

    ca_administrative_email = fields.Char(string="Administrative Email")
    ca_administrative_phone = fields.Char(string="Administrative Phone")
    ca_administrative_website = fields.Char(string="Administrative Website")
    ca_legal_representative_id = fields.Many2one("res.partner", string="Legal Representative")
    ca_legal_representative_function = fields.Char(string="Legal Representative Function")
    ca_administrative_notes = fields.Text(string="Administrative Notes")

    ca_administrative_document_ids = fields.Many2many(
        "ir.attachment",
        "ca_company_profile_admin_document_rel",
        "company_id",
        "attachment_id",
        string="Administrative Documents",
    )

    @api.constrains("ca_share_capital")
    def _check_share_capital(self):
        for company in self:
            if company.ca_share_capital is not False and company.ca_share_capital < 0:
                raise ValidationError(_("The share capital cannot be negative."))

    @api.constrains(
        "ca_incorporation_date",
        "ca_activity_start_date",
        "ca_nif_date",
        "ca_nif_expiry",
        "ca_nis_date",
        "ca_nis_expiry",
        "ca_rc_date",
        "ca_rc_expiry",
        "ca_tax_article_date",
        "ca_tax_article_expiry",
        "ca_casnos_date",
        "ca_casnos_expiry",
        "ca_cnas_date",
        "ca_cnas_expiry",
        "ca_approval_date",
        "ca_approval_expiry",
        "ca_vat_start_date",
        "ca_vat_end_date",
    )
    def _check_dates(self):
        for company in self:
            if company.ca_incorporation_date and company.ca_activity_start_date and company.ca_activity_start_date < company.ca_incorporation_date:
                raise ValidationError(_("The activity start date cannot be earlier than the incorporation date."))
            pairs = [
                (company.ca_nif_date, company.ca_nif_expiry),
                (company.ca_nis_date, company.ca_nis_expiry),
                (company.ca_rc_date, company.ca_rc_expiry),
                (company.ca_tax_article_date, company.ca_tax_article_expiry),
                (company.ca_casnos_date, company.ca_casnos_expiry),
                (company.ca_cnas_date, company.ca_cnas_expiry),
                (company.ca_approval_date, company.ca_approval_expiry),
                (company.ca_vat_start_date, company.ca_vat_end_date),
            ]
            for start, end in pairs:
                if start and end and end < start:
                    raise ValidationError(_("The end date cannot be earlier than the start date."))

    @api.constrains("ca_legal_form_id", "ca_legal_description")
    def _check_legal_form_description(self):
        # Placeholder for future validated rules.
        return
