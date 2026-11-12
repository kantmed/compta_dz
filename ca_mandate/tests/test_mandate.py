from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCaMandate(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env["res.company"].create({"name": "Client A"})
        cls.company_b = cls.env["res.company"].create({"name": "Client B"})
        cls.firm = cls.env["res.company"].create({"name": "Firm"})

        cls.group_user = cls.env.ref("ca_core.group_ca_core_user")
        cls.group_manager = cls.env.ref("ca_core.group_ca_core_manager")
        cls.group_admin = cls.env.ref("ca_core.group_ca_core_admin")

        cls.user_firm = cls.env["res.users"].create(
            {
                "name": "Firm User",
                "login": "ca_mandate_firm_user",
                "company_id": cls.firm.id,
                "company_ids": [Command.set([cls.firm.id, cls.company_a.id])],
                "group_ids": [Command.set([cls.group_user.id])],
            }
        )
        cls.manager_firm = cls.env["res.users"].create(
            {
                "name": "Firm Manager",
                "login": "ca_mandate_firm_manager",
                "company_id": cls.firm.id,
                "company_ids": [Command.set([cls.firm.id, cls.company_a.id])],
                "group_ids": [Command.set([cls.group_manager.id])],
            }
        )
        cls.admin_firm = cls.env["res.users"].create(
            {
                "name": "Firm Admin",
                "login": "ca_mandate_firm_admin",
                "company_id": cls.firm.id,
                "company_ids": [Command.set([cls.firm.id, cls.company_a.id])],
                "group_ids": [Command.set([cls.group_admin.id])],
            }
        )
        cls.user_other = cls.env["res.users"].create(
            {
                "name": "Other User",
                "login": "ca_mandate_other_user",
                "company_id": cls.company_b.id,
                "company_ids": [Command.set([cls.company_b.id])],
                "group_ids": [Command.set([cls.group_user.id])],
            }
        )

        cls.folder_a = cls.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Folder A",
                "code": "FOLDER-A",
                "company_id": cls.company_a.id,
                "manager_id": cls.env.user.id,
            }
        )
        cls.folder_b = cls.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Folder B",
                "code": "FOLDER-B",
                "company_id": cls.company_b.id,
                "manager_id": cls.env.user.id,
            }
        )

    def _create_mandate(self, **kwargs):
        vals = {
            "name": "Test Mandate",
            "company_id": self.company_a.id,
            "firm_id": self.firm.id,
            "date_start": "2026-01-01",
            "date_end": "2026-12-31",
            "manager_id": self.manager_firm.id,
        }
        vals.update(kwargs)
        return self.env["ca.mandate"].create(vals)

    def test_create_mandate(self):
        mandate = self._create_mandate()
        self.assertTrue(mandate.reference)
        self.assertEqual(mandate.state, "draft")

    def test_reference_generated(self):
        mandate = self._create_mandate()
        self.assertNotEqual(mandate.reference, "New")

    def test_company_firm_different(self):
        with self.assertRaises(ValidationError):
            self._create_mandate(firm_id=self.company_a.id)

    def test_folder_company_coherence(self):
        with self.assertRaises(ValidationError):
            self._create_mandate(folder_ids=[Command.set([self.folder_b.id])])

    def test_dates_coherence(self):
        with self.assertRaises(ValidationError):
            self._create_mandate(date_start="2026-02-01", date_end="2026-01-01")

    def test_status_transitions(self):
        mandate = self._create_mandate()
        mandate.action_submit()
        self.assertEqual(mandate.state, "pending")
        mandate.action_validate()
        self.assertEqual(mandate.state, "active")
        mandate.action_suspend()
        self.assertEqual(mandate.state, "suspended")
        mandate.action_resume()
        self.assertEqual(mandate.state, "active")
        mandate.action_done()
        self.assertEqual(mandate.state, "done")

    def test_forbidden_transitions(self):
        mandate = self._create_mandate()
        with self.assertRaises(ValidationError):
            mandate.write({"state": "active"})
        mandate.action_submit()
        mandate.action_validate()
        mandate.action_done()
        with self.assertRaises(ValidationError):
            mandate.write({"state": "active"})

    def test_cancelled_mandate_not_reactivatable(self):
        mandate = self._create_mandate()
        mandate.action_submit()
        mandate.action_cancel()
        self.assertEqual(mandate.state, "cancelled")
        with self.assertRaises(ValidationError):
            mandate.action_validate()

    def test_active_mandate_not_deletable(self):
        mandate = self._create_mandate()
        mandate.action_submit()
        mandate.action_validate()
        with self.assertRaises(ValidationError):
            mandate.unlink()

    def test_primary_mandate_conflict(self):
        mandate1 = self._create_mandate(is_primary=True)
        mandate1.action_submit()
        mandate1.action_validate()
        with self.assertRaises(ValidationError):
            self._create_mandate(is_primary=True).action_submit()

    def test_collaborator_access(self):
        mandate = self._create_mandate()
        collaborator = self.env["ca.mandate.collaborator"].create(
            {
                "mandate_id": mandate.id,
                "user_id": self.user_firm.id,
                "role": "Reviewer",
            }
        )
        self.assertEqual(collaborator.user_id, self.user_firm)
        self.assertIn(collaborator, mandate.collaborator_ids)

    def test_collaborator_firm_coherence(self):
        with self.assertRaises(ValidationError):
            self.env["ca.mandate.collaborator"].create(
                {
                    "mandate_id": self._create_mandate().id,
                    "user_id": self.user_other.id,
                    "role": "Reviewer",
                }
            )

    def test_user_access(self):
        mandate = self._create_mandate()
        mandate.collaborator_ids = [Command.create({"user_id": self.user_firm.id, "role": "Reviewer"})]
        self.assertTrue(mandate.with_user(self.user_firm).has_access("read"))

    def test_other_user_denied(self):
        mandate = self._create_mandate()
        with self.assertRaises(Exception):
            mandate.with_user(self.user_other).read(["name"])

    def test_manager_access(self):
        mandate = self._create_mandate()
        self.assertTrue(mandate.with_user(self.manager_firm).has_access("write"))

    def test_admin_access(self):
        mandate = self._create_mandate()
        self.assertTrue(mandate.with_user(self.admin_firm).has_access("write"))

    def test_document_access_allowed(self):
        mandate = self._create_mandate()
        attachment = self.env["ir.attachment"].sudo().create(
            {
                "name": "contract.pdf",
                "raw": b"test",
                "res_model": "ca.mandate",
                "res_id": mandate.id,
            }
        )
        self.assertEqual(attachment.with_user(self.manager_firm).name, attachment.name)

    def test_document_access_denied(self):
        mandate = self._create_mandate()
        attachment = self.env["ir.attachment"].sudo().create(
            {
                "name": "contract.pdf",
                "raw": b"test",
                "res_model": "ca.mandate",
                "res_id": mandate.id,
            }
        )
        with self.assertRaises(Exception):
            attachment.with_user(self.user_other).read(["name"])

    def test_collaborator_real_access(self):
        mandate = self._create_mandate()
        mandate.collaborator_ids = [Command.create({"user_id": self.user_firm.id, "role": "Reviewer"})]
        self.assertEqual(mandate.with_user(self.user_firm).name, mandate.name)

    def test_non_collaborator_denied(self):
        mandate = self._create_mandate()
        with self.assertRaises(Exception):
            mandate.with_user(self.user_other).read(["name"])

    def test_suspended_mandate_remains_readable_by_manager(self):
        mandate = self._create_mandate()
        mandate.action_submit()
        mandate.action_validate()
        mandate.action_suspend()
        self.assertEqual(mandate.with_user(self.manager_firm).state, "suspended")

    def test_installation(self):
        module = self.env["ir.module.module"].search([("name", "=", "ca_mandate")])
        self.assertEqual(module.state, "installed")

    def test_successor_company_coherence(self):
        mandate1 = self._create_mandate()
        with self.assertRaises(ValidationError):
            self._create_mandate(company_id=self.company_b.id, previous_mandate_id=mandate1.id)
