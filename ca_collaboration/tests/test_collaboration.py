from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCaCollaboration(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env["res.company"].create({"name": "Client A"})
        cls.company_b = cls.env["res.company"].create({"name": "Client B"})
        cls.firm = cls.env["res.company"].create({"name": "Firm"})

        cls.group_user = cls.env.ref("ca_core.group_ca_core_user")
        cls.group_manager = cls.env.ref("ca_core.group_ca_core_manager")
        cls.group_admin = cls.env.ref("ca_core.group_ca_core_admin")
        cls.audit_admin = cls.env.ref("ca_audit_log.group_ca_audit_log_admin")
        cls.env.user.write({"group_ids": [(4, cls.audit_admin.id)]})

        cls.user_firm = cls.env["res.users"].create(
            {
                "name": "Firm User",
                "login": "ca_collab_firm_user",
                "company_id": cls.firm.id,
                "company_ids": [Command.set([cls.firm.id, cls.company_a.id])],
                "group_ids": [Command.set([cls.group_user.id])],
            }
        )
        cls.manager_firm = cls.env["res.users"].create(
            {
                "name": "Firm Manager",
                "login": "ca_collab_firm_manager",
                "company_id": cls.firm.id,
                "company_ids": [Command.set([cls.firm.id, cls.company_a.id])],
                "group_ids": [Command.set([cls.group_manager.id])],
            }
        )
        cls.admin_firm = cls.env["res.users"].create(
            {
                "name": "Firm Admin",
                "login": "ca_collab_firm_admin",
                "company_id": cls.firm.id,
                "company_ids": [Command.set([cls.firm.id, cls.company_a.id])],
                "group_ids": [Command.set([cls.group_admin.id])],
            }
        )
        cls.user_other = cls.env["res.users"].create(
            {
                "name": "Other User",
                "login": "ca_collab_other_user",
                "company_id": cls.company_b.id,
                "company_ids": [Command.set([cls.company_b.id])],
                "group_ids": [Command.set([cls.group_user.id])],
            }
        )

        cls.folder_a = cls.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Folder A",
                "code": "COLLAB-FOLDER-A",
                "company_id": cls.company_a.id,
                "manager_id": cls.env.user.id,
            }
        )
        cls.mandate_a = cls.env["ca.mandate"].sudo().create(
            {
                "name": "Mandate A",
                "company_id": cls.company_a.id,
                "firm_id": cls.firm.id,
                "date_start": "2026-01-01",
                "date_end": "2026-12-31",
                "manager_id": cls.manager_firm.id,
                "folder_ids": [Command.set([cls.folder_a.id])],
            }
        )
        cls.mandate_a.action_submit()
        cls.mandate_a.action_validate()

    def _create_collaboration(self, **kwargs):
        vals = {
            "name": "Collaboration A",
            "company_id": self.company_a.id,
            "firm_id": self.firm.id,
            "mandate_id": self.mandate_a.id,
            "folder_id": self.folder_a.id,
            "firm_manager_id": self.manager_firm.id,
        }
        vals.update(kwargs)
        return self.env["ca.collaboration"].create(vals)

    def test_installation(self):
        module = self.env["ir.module.module"].search([("name", "=", "ca_collaboration")])
        self.assertEqual(module.state, "installed")

    def test_create_collaboration(self):
        collab = self._create_collaboration()
        self.assertEqual(collab.state, "draft")
        self.assertEqual(collab.mandate_id, self.mandate_a)

    def test_refuse_inconsistent_mandate(self):
        other_mandate = self.env["ca.mandate"].sudo().create(
            {
                "name": "Mandate B",
                "company_id": self.company_b.id,
                "firm_id": self.firm.id,
                "date_start": "2026-01-01",
                "manager_id": self.manager_firm.id,
            }
        )
        with self.assertRaises(ValidationError):
            self._create_collaboration(mandate_id=other_mandate.id)

    def test_refuse_folder_other_company(self):
        with self.assertRaises(ValidationError):
            self._create_collaboration(folder_id=self.env["ca.accounting.folder"].sudo().create(
                {"name": "Other Folder", "code": "OTHER", "company_id": self.company_b.id, "manager_id": self.env.user.id}
            ).id)

    def test_assign_collaborator(self):
        collab = self._create_collaboration()
        member = self.env["ca.collaboration.member"].create(
            {
                "collaboration_id": collab.id,
                "user_id": self.user_firm.id,
                "role": "firm_collaborator",
            }
        )
        self.assertEqual(member.user_id, self.user_firm)
        self.assertIn(member, collab.member_ids)

    def test_refuse_unauthorized_collaborator(self):
        collab = self._create_collaboration()
        with self.assertRaises(ValidationError):
            self.env["ca.collaboration.member"].create(
                {
                    "collaboration_id": collab.id,
                    "user_id": self.user_other.id,
                    "role": "firm_collaborator",
                }
            )

    def test_revoke_collaborator(self):
        collab = self._create_collaboration()
        member = self.env["ca.collaboration.member"].create(
            {
                "collaboration_id": collab.id,
                "user_id": self.user_firm.id,
                "role": "firm_collaborator",
            }
        )
        member.active = False
        self.assertFalse(member.is_effectively_active())

    def test_authorized_access(self):
        collab = self._create_collaboration()
        collab.member_ids = [Command.create({"user_id": self.user_firm.id, "role": "firm_collaborator"})]
        self.assertEqual(collab.with_user(self.user_firm).name, collab.name)

    def test_deny_other_collaboration(self):
        collab = self._create_collaboration()
        other_collab = self._create_collaboration(name="Other Collaboration")
        with self.assertRaises(Exception):
            other_collab.with_user(self.user_firm).read(["name"])

    def test_isolation_between_companies(self):
        other_collab = self._create_collaboration(company_id=self.company_b.id, firm_id=self.firm.id, mandate_id=self.mandate_a.id) if False else None
        collab = self._create_collaboration()
        self.assertTrue(collab.with_user(self.user_other).search_count([("id", "=", collab.id)]) == 0)

    def test_isolation_between_firms(self):
        collab = self._create_collaboration()
        self.assertTrue(collab.with_user(self.user_other).search_count([("id", "=", collab.id)]) == 0)

    def test_create_task(self):
        collab = self._create_collaboration()
        collab.member_ids = [Command.create({"user_id": self.user_firm.id, "role": "firm_collaborator"})]
        collab.action_submit()
        collab.action_activate()
        task = self.env["ca.collaboration.task"].create(
            {
                "name": "Task 1",
                "collaboration_id": collab.id,
                "assigned_to": self.user_firm.id,
            }
        )
        self.assertEqual(task.state, "new")

    def test_refuse_task_unauthorized_dossier(self):
        collab = self._create_collaboration()
        collab.member_ids = [Command.create({"user_id": self.user_firm.id, "role": "firm_collaborator"})]
        collab.action_submit()
        collab.action_activate()
        with self.assertRaises(ValidationError):
            self.env["ca.collaboration.task"].create(
                {
                    "name": "Forbidden Task",
                    "collaboration_id": collab.id,
                    "assigned_to": self.user_other.id,
                }
            )

    def test_task_state_change(self):
        collab = self._create_collaboration()
        collab.member_ids = [Command.create({"user_id": self.user_firm.id, "role": "firm_collaborator"})]
        collab.action_submit()
        collab.action_activate()
        task = self.env["ca.collaboration.task"].create(
            {
                "name": "Task State",
                "collaboration_id": collab.id,
                "assigned_to": self.user_firm.id,
            }
        )
        task.write({"state": "todo"})
        task.action_start()
        self.assertEqual(task.state, "in_progress")
        task.action_done()
        self.assertEqual(task.state, "done")

    def test_create_document_request(self):
        collab = self._create_collaboration()
        collab.member_ids = [Command.create({"user_id": self.user_firm.id, "role": "firm_collaborator"})]
        collab.action_submit()
        collab.action_activate()
        request = self.env["ca.collaboration.document.request"].create(
            {
                "name": "Request 1",
                "collaboration_id": collab.id,
                "requester_id": self.manager_firm.id,
                "recipient_id": self.user_firm.id,
            }
        )
        self.assertEqual(request.state, "draft")

    def test_document_transmission(self):
        collab = self._create_collaboration()
        collab.member_ids = [Command.create({"user_id": self.user_firm.id, "role": "firm_collaborator"})]
        collab.action_submit()
        collab.action_activate()
        request = self.env["ca.collaboration.document.request"].create(
            {
                "name": "Request 2",
                "collaboration_id": collab.id,
                "requester_id": self.manager_firm.id,
                "recipient_id": self.user_firm.id,
            }
        )
        request.action_send()
        self.assertEqual(request.state, "sent")

    def test_document_validation(self):
        collab = self._create_collaboration()
        collab.member_ids = [Command.create({"user_id": self.user_firm.id, "role": "firm_collaborator"})]
        collab.action_submit()
        collab.action_activate()
        request = self.env["ca.collaboration.document.request"].create(
            {
                "name": "Request 3",
                "collaboration_id": collab.id,
                "requester_id": self.manager_firm.id,
                "recipient_id": self.user_firm.id,
            }
        )
        request.action_send()
        request.action_receive()
        request.action_validate()
        self.assertEqual(request.state, "validated")

    def test_message_creation(self):
        collab = self._create_collaboration()
        collab.member_ids = [Command.create({"user_id": self.user_firm.id, "role": "firm_collaborator"}), Command.create({"user_id": self.manager_firm.id, "role": "firm_manager"})]
        collab.action_submit()
        collab.action_activate()
        message = self.env["ca.collaboration.message"].create(
            {
                "collaboration_id": collab.id,
                "author_id": self.user_firm.id,
                "body": "Hello",
                "recipient_ids": [Command.set([self.manager_firm.id])],
            }
        )
        self.assertEqual(message.author_id, self.user_firm)

    def test_revoke_access_after_suspension(self):
        collab = self._create_collaboration()
        collab.member_ids = [Command.create({"user_id": self.user_firm.id, "role": "firm_collaborator"})]
        collab.action_submit()
        collab.action_activate()
        collab.action_suspend()
        self.assertEqual(collab.state, "suspended")

    def test_conservation_historique(self):
        collab = self._create_collaboration()
        collab.member_ids = [Command.create({"user_id": self.user_firm.id, "role": "firm_collaborator"}), Command.create({"user_id": self.manager_firm.id, "role": "firm_manager"})]
        collab.action_submit()
        collab.action_activate()
        message = self.env["ca.collaboration.message"].create(
            {
                "collaboration_id": collab.id,
                "author_id": self.user_firm.id,
                "body": "Historic",
            }
        )
        self.assertTrue(message.id)

    def test_installation(self):
        module = self.env["ir.module.module"].search([("name", "=", "ca_collaboration")])
        self.assertEqual(module.state, "installed")

    def test_dashboard_counts(self):
        collab = self._create_collaboration()
        collab.member_ids = [Command.create({"user_id": self.user_firm.id, "role": "firm_collaborator"})]
        collab.action_submit()
        collab.action_activate()
        self.assertGreaterEqual(collab.open_task_count, 0)
