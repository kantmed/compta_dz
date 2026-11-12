from odoo import Command
from odoo.exceptions import ValidationError
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCaCompanyProfile(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env["res.company"].create({"name": "Profile Company"})
        cls.legal_form = cls.env["ca.legal.form"].create({"code": "TESTLF", "name": "Test Legal Form"})

    def test_create_profile(self):
        self.company.write(
            {
                "ca_legal_form_id": self.legal_form.id,
                "ca_trade_name": "Trade",
                "ca_incorporation_date": "2020-01-01",
                "ca_activity_start_date": "2020-02-01",
                "ca_share_capital": 100000.0,
                "ca_legal_state": "active",
                "ca_nif": "NIF123",
            }
        )
        self.assertEqual(self.company.ca_legal_form_id, self.legal_form)
        self.assertEqual(self.company.ca_legal_state, "active")

    def test_negative_share_capital(self):
        with self.assertRaises(ValidationError):
            self.company.write({"ca_share_capital": -1.0})

    def test_date_coherence(self):
        with self.assertRaises(ValidationError):
            self.company.write(
                {
                    "ca_incorporation_date": "2020-02-01",
                    "ca_activity_start_date": "2020-01-01",
                }
            )

    def test_identifier_date_coherence(self):
        with self.assertRaises(ValidationError):
            self.company.write(
                {
                    "ca_nif_date": "2026-02-01",
                    "ca_nif_expiry": "2026-01-01",
                }
            )

    def test_audit_log_created(self):
        before = self.env["ca.audit.log"].search_count([])
        self.company.write({"ca_trade_name": "Audited Trade"})
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)

    def test_multi_company_isolation(self):
        other_company = self.env["res.company"].create({"name": "Other Profile Company"})
        self.assertTrue(other_company.id != self.company.id)
        self.assertEqual(self.company.ca_legal_state, "active")

    def test_optional_identifiers(self):
        company = self.env["res.company"].create({"name": "Optional Company"})
        self.assertFalse(company.ca_nif)
        self.assertFalse(company.ca_nis)

    def test_legal_representative(self):
        partner = self.env["res.partner"].create({"name": "Legal Rep"})
        self.company.write({"ca_legal_representative_id": partner.id, "ca_legal_representative_function": "Manager"})
        self.assertEqual(self.company.ca_legal_representative_id, partner)

    def test_documents(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "profile.pdf",
                "raw": b"test",
                "res_model": "res.company",
                "res_id": self.company.id,
            }
        )
        self.company.write({"ca_administrative_document_ids": [Command.link(attachment.id)]})
        self.assertIn(attachment, self.company.ca_administrative_document_ids)

    def test_multi_company_profile_isolation(self):
        other_company = self.env["res.company"].create({"name": "Other Isolated Company"})
        user = self.env["res.users"].create(
            {
                "name": "Isolated User",
                "login": "ca_company_profile_isolated",
                "company_id": other_company.id,
                "company_ids": [(6, 0, [other_company.id])],
                "group_ids": [(6, 0, [self.env.ref("base.group_user").id])],
            }
        )
        with self.assertRaises(AccessError):
            self.company.with_user(user).read(["ca_trade_name"])
        with self.assertRaises(AccessError):
            self.company.with_user(user).write({"ca_trade_name": "Forbidden"})

    def test_attachment_access(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "company-profile.pdf",
                "raw": b"test",
                "res_model": "res.company",
                "res_id": self.company.id,
            }
        )
        other_company = self.env["res.company"].create({"name": "Attachment Company"})
        other_user = self.env["res.users"].create(
            {
                "name": "Attachment User",
                "login": "ca_company_profile_attachment",
                "company_id": other_company.id,
                "company_ids": [(6, 0, [other_company.id])],
                "group_ids": [(6, 0, [self.env.ref("base.group_user").id])],
            }
        )
        with self.assertRaises(AccessError):
            attachment.with_user(other_user).read(["name"])

    def test_audit_log_protection(self):
        log = self.env["ca.audit.log"].sudo().create(
            {
                "company_id": self.company.id,
                "model_name": "res.company",
                "operation": "write",
                "description": "profile update",
            }
        )
        other_company = self.env["res.company"].create({"name": "Audit Company"})
        other_user = self.env["res.users"].create(
            {
                "name": "Audit User",
                "login": "ca_company_profile_audit",
                "company_id": other_company.id,
                "company_ids": [(6, 0, [other_company.id])],
                "group_ids": [(6, 0, [self.env.ref("base.group_user").id])],
            }
        )
        with self.assertRaises(AccessError):
            log.with_user(other_user).read(["description"])
        with self.assertRaises(AccessError):
            log.with_user(other_user).write({"description": "changed"})
        with self.assertRaises(AccessError):
            log.with_user(other_user).unlink()

    def test_audit_log_created_on_profile_update(self):
        before = self.env["ca.audit.log"].sudo().search_count([])
        self.company.write({"ca_trade_name": "Audited Profile"})
        after = self.env["ca.audit.log"].sudo().search_count([])
        self.assertGreater(after, before)

    def test_installation(self):
        module = self.env["ir.module.module"].search([("name", "=", "ca_company_profile")])
        self.assertEqual(module.state, "installed")
