from psycopg2 import IntegrityError

from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCaAccountingFolder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env["res.company"].create({"name": "Company A"})
        cls.company_b = cls.env["res.company"].create({"name": "Company B"})

        cls.group_user = cls.env.ref("ca_core.group_ca_core_user")
        cls.group_manager = cls.env.ref("ca_core.group_ca_core_manager")
        cls.group_admin = cls.env.ref("ca_core.group_ca_core_admin")

        cls.user_a = cls.env["res.users"].create(
            {
                "name": "User A",
                "login": "ca_test_user_a",
                "company_id": cls.company_a.id,
                "company_ids": [Command.set([cls.company_a.id])],
                "group_ids": [Command.set([cls.group_user.id])],
            }
        )
        cls.manager_a = cls.env["res.users"].create(
            {
                "name": "Manager A",
                "login": "ca_test_manager_a",
                "company_id": cls.company_a.id,
                "company_ids": [Command.set([cls.company_a.id])],
                "group_ids": [Command.set([cls.group_manager.id])],
            }
        )
        cls.admin_a = cls.env["res.users"].create(
            {
                "name": "Admin A",
                "login": "ca_test_admin_a",
                "company_id": cls.company_a.id,
                "company_ids": [Command.set([cls.company_a.id])],
                "group_ids": [Command.set([cls.group_admin.id])],
            }
        )
        cls.user_b = cls.env["res.users"].create(
            {
                "name": "User B",
                "login": "ca_test_user_b",
                "company_id": cls.company_b.id,
                "company_ids": [Command.set([cls.company_b.id])],
                "group_ids": [Command.set([cls.group_user.id])],
            }
        )
        cls.manager_ab = cls.env["res.users"].create(
            {
                "name": "Manager AB",
                "login": "ca_test_manager_ab",
                "company_id": cls.company_a.id,
                "company_ids": [Command.set([cls.company_a.id, cls.company_b.id])],
                "group_ids": [Command.set([cls.group_manager.id])],
            }
        )
        cls.admin_ab = cls.env["res.users"].create(
            {
                "name": "Admin AB",
                "login": "ca_test_admin_ab",
                "company_id": cls.company_a.id,
                "company_ids": [Command.set([cls.company_a.id, cls.company_b.id])],
                "group_ids": [Command.set([cls.group_admin.id])],
            }
        )

    def _create_folder(self, company=None, manager=None, code="FOLDER-1", **kwargs):
        company = company or self.company_a
        manager = manager or self.manager_a
        vals = {
            "name": "Test Folder",
            "code": code,
            "company_id": company.id,
            "manager_id": manager.id,
        }
        vals.update(kwargs)
        return self.env["ca.accounting.folder"].create(vals)

    def test_create_valid_folder(self):
        folder = self._create_folder()
        self.assertEqual(folder.state, "draft")
        self.assertEqual(folder.company_id, self.company_a)

    def test_refuse_without_company(self):
        with self.assertRaises(ValidationError):
            self.env["ca.accounting.folder"].create(
                {
                    "name": "No Company",
                    "code": "NO-COMPANY",
                    "company_id": False,
                    "manager_id": self.manager_a.id,
                }
            )

    def test_refuse_without_manager(self):
        with self.assertRaises(ValidationError):
            self.env["ca.accounting.folder"].create(
                {
                    "name": "No Manager",
                    "code": "NO-MANAGER",
                    "company_id": self.company_a.id,
                    "manager_id": False,
                }
            )

    def test_create_forbidden_initial_status(self):
        for state in ("active", "review", "closed", "archived"):
            with self.subTest(state=state), self.assertRaises(ValidationError):
                self.env["ca.accounting.folder"].create(
                    {
                        "name": "Forbidden Status",
                        "code": "FORBIDDEN-STATUS-" + state.upper(),
                        "company_id": self.company_a.id,
                        "manager_id": self.manager_a.id,
                        "state": state,
                    }
                )

    def test_duplicate_code_same_company(self):
        self._create_folder(code="DUPLICATE")
        with self.assertRaises(IntegrityError):
            self._create_folder(code="DUPLICATE")

    def test_same_code_different_company(self):
        self._create_folder(company=self.company_a, code="SAME-CODE")
        folder_b = self._create_folder(company=self.company_b, manager=self.user_b, code="SAME-CODE")
        self.assertEqual(folder_b.company_id, self.company_b)

    def test_manager_company_coherence(self):
        with self.assertRaises(ValidationError):
            self._create_folder(company=self.company_b, manager=self.manager_a)

    def test_collaborator_company_coherence(self):
        with self.assertRaises(ValidationError):
            self._create_folder(collaborator_ids=[Command.set([self.user_b.id])])

    def test_closing_date_before_opening(self):
        with self.assertRaises(ValidationError):
            self._create_folder(
                opening_date="2026-02-01",
                closing_date="2026-01-01",
            )

    def test_status_transitions(self):
        folder = self._create_folder()
        folder.action_activate()
        self.assertEqual(folder.state, "active")
        folder.action_review()
        self.assertEqual(folder.state, "review")
        folder.action_close()
        self.assertEqual(folder.state, "closed")
        folder.action_archive()
        self.assertEqual(folder.state, "archived")
        with self.assertRaises(ValidationError):
            folder.action_activate()

    def test_forbidden_transitions(self):
        folder = self._create_folder()
        with self.assertRaises(ValidationError):
            folder.write({"state": "closed"})
        folder.action_activate()
        with self.assertRaises(ValidationError):
            folder.write({"state": "archived"})
        folder.action_close()
        folder.action_archive()
        with self.assertRaises(ValidationError):
            folder.write({"state": "active"})

    def test_manager_effective_crud(self):
        folder = self._create_folder()
        folder.with_user(self.manager_a).write({"description": "manager update"})
        self.assertEqual(folder.description, "manager update")
        folder.with_user(self.manager_a).unlink()
        self.assertFalse(folder.exists())

    def test_admin_effective_crud(self):
        folder = self._create_folder()
        folder.with_user(self.admin_a).write({"description": "admin update"})
        self.assertEqual(folder.description, "admin update")
        folder.with_user(self.admin_a).unlink()
        self.assertFalse(folder.exists())

    def test_user_effective_read_only(self):
        folder = self._create_folder(collaborator_ids=[Command.set([self.user_a.id])])
        self.assertEqual(folder.with_user(self.user_a).name, folder.name)
        with self.assertRaises(AccessError):
            folder.with_user(self.user_a).write({"description": "no"})
        with self.assertRaises(AccessError):
            self.env["ca.accounting.folder"].with_user(self.user_a).create(
                {"name": "X", "code": "X", "company_id": self.company_a.id, "manager_id": self.manager_a.id}
            )

    def test_limits_of_company_ids(self):
        user = self.env["res.users"].create(
            {
                "name": "Limited User",
                "login": "ca_test_limited",
                "company_id": self.company_a.id,
                "company_ids": [Command.set([self.company_a.id])],
                "group_ids": [Command.set([self.group_user.id])],
            }
        )
        folder_b = self._create_folder(company=self.company_b, manager=self.user_b, code="LIMITED-B")
        with self.assertRaises(AccessError):
            folder_b.with_user(user).read(["name"])

    def test_change_responsible(self):
        folder = self._create_folder()
        folder.write({"manager_id": self.admin_a.id})
        self.assertEqual(folder.manager_id, self.admin_a)

    def test_change_collaborators(self):
        folder = self._create_folder()
        folder.write({"collaborator_ids": [Command.set([self.user_a.id])]})
        self.assertIn(self.user_a, folder.collaborator_ids)

    def test_archived_access_by_unassigned_user(self):
        folder = self._create_folder()
        folder.action_activate()
        folder.action_close()
        folder.action_archive()
        with self.assertRaises(AccessError):
            folder.with_user(self.user_b).read(["name"])

    def test_multi_record_create_denied(self):
        with self.assertRaises(AccessError):
            self.env["ca.accounting.folder"].with_user(self.user_a).create(
                [
                    {
                        "name": "Bulk 1",
                        "code": "BULK-1",
                        "company_id": self.company_a.id,
                        "manager_id": self.manager_a.id,
                    },
                    {
                        "name": "Bulk 2",
                        "code": "BULK-2",
                        "company_id": self.company_a.id,
                        "manager_id": self.manager_a.id,
                    },
                ]
            )

    def test_manager_can_create_folder(self):
        folder = self.env["ca.accounting.folder"].with_user(self.manager_a).create(
            {
                "name": "Manager Created",
                "code": "MANAGER-CREATE",
                "company_id": self.company_a.id,
                "manager_id": self.manager_a.id,
            }
        )
        self.assertEqual(folder.manager_id, self.manager_a)
        self.assertEqual(folder.company_id, self.company_a)

    def test_admin_can_create_folder(self):
        folder = self.env["ca.accounting.folder"].with_user(self.admin_a).create(
            {
                "name": "Admin Created",
                "code": "ADMIN-CREATE",
                "company_id": self.company_a.id,
                "manager_id": self.admin_a.id,
            }
        )
        self.assertEqual(folder.manager_id, self.admin_a)
        self.assertEqual(folder.company_id, self.company_a)

    def test_manager_can_create_folder_in_authorized_second_company(self):
        folder = self.env["ca.accounting.folder"].with_user(self.manager_ab).create(
            {
                "name": "Manager Second Company",
                "code": "MANAGER-SECOND",
                "company_id": self.company_b.id,
                "manager_id": self.manager_ab.id,
            }
        )
        self.assertEqual(folder.company_id, self.company_b)

    def test_manager_cannot_create_folder_in_unauthorized_company(self):
        with self.assertRaises((AccessError, ValidationError)):
            self.env["ca.accounting.folder"].with_user(self.manager_a).create(
                {
                    "name": "Forbidden Company",
                    "code": "FORBIDDEN-COMPANY",
                    "company_id": self.company_b.id,
                    "manager_id": self.manager_a.id,
                }
            )

    def test_archived_folder_not_modifiable(self):
        folder = self._create_folder()
        folder.action_activate()
        folder.action_close()
        folder.action_archive()
        with self.assertRaises(ValidationError):
            folder.with_user(self.manager_a).write({"description": "changed"})

    def test_archived_folder_not_deletable_by_manager(self):
        folder = self._create_folder()
        folder.action_activate()
        folder.action_close()
        folder.action_archive()
        with self.assertRaises(ValidationError):
            folder.with_user(self.manager_a).unlink()

    def test_archived_folder_readable_by_authorized_user(self):
        folder = self._create_folder(collaborator_ids=[Command.set([self.user_a.id])])
        folder.action_activate()
        folder.action_close()
        folder.action_archive()
        self.assertEqual(folder.with_user(self.user_a).name, folder.name)

    def test_manager_can_create_and_update(self):
        folder = self._create_folder().with_user(self.manager_a)
        folder.write({"description": "updated by manager"})
        self.assertEqual(folder.description, "updated by manager")

    def test_manager_can_delete(self):
        folder = self._create_folder()
        folder.with_user(self.manager_a).unlink()
        self.assertFalse(folder.exists())

    def test_user_read_assigned_folder(self):
        folder = self._create_folder(collaborator_ids=[Command.set([self.user_a.id])])
        read_folder = folder.with_user(self.user_a)
        self.assertEqual(read_folder.name, folder.name)

    def test_user_cannot_read_unassigned_folder(self):
        folder = self._create_folder()
        with self.assertRaises(AccessError):
            folder.with_user(self.user_a).read(["name"])

    def test_user_cannot_create_folder(self):
        with self.assertRaises(AccessError):
            self.env["ca.accounting.folder"].with_user(self.user_a).create(
                {
                    "name": "Forbidden",
                    "code": "FORBIDDEN",
                    "company_id": self.company_a.id,
                    "manager_id": self.manager_a.id,
                }
            )

    def test_user_cannot_update_folder(self):
        folder = self._create_folder(collaborator_ids=[Command.set([self.user_a.id])])
        with self.assertRaises(AccessError):
            folder.with_user(self.user_a).write({"description": "forbidden"})

    def test_user_cannot_change_manager(self):
        folder = self._create_folder(collaborator_ids=[Command.set([self.user_a.id])])
        with self.assertRaises(AccessError):
            folder.with_user(self.user_a).write({"manager_id": self.user_a.id})

    def test_user_cannot_change_collaborators(self):
        folder = self._create_folder(collaborator_ids=[Command.set([self.user_a.id])])
        with self.assertRaises(AccessError):
            folder.with_user(self.user_a).write({"collaborator_ids": [Command.link(self.user_b.id)]})

    def test_user_cannot_add_self_to_unauthorized_folder(self):
        folder = self._create_folder()
        with self.assertRaises(AccessError):
            folder.with_user(self.user_a).write({"collaborator_ids": [Command.link(self.user_a.id)]})

    def test_user_cannot_change_company(self):
        folder = self._create_folder(collaborator_ids=[Command.set([self.user_a.id])])
        with self.assertRaises((ValidationError, AccessError)):
            folder.with_user(self.manager_a).write({"company_id": self.company_b.id})

    def test_company_immutability_unauthorized_manager(self):
        folder = self._create_folder()
        with self.assertRaises(ValidationError):
            folder.with_user(self.manager_a).write({"company_id": self.company_b.id})

    def test_company_immutability_authorized_manager_both_companies(self):
        folder = self._create_folder(manager=self.manager_ab)
        with self.assertRaises(ValidationError):
            folder.write({"company_id": self.company_b.id})

    def test_company_immutability_simultaneous_company_and_manager(self):
        folder = self._create_folder(manager=self.manager_ab)
        with self.assertRaises(ValidationError):
            folder.write({"company_id": self.company_b.id, "manager_id": self.manager_ab.id})

    def test_company_immutability_by_manager(self):
        folder = self._create_folder()
        with self.assertRaises(ValidationError):
            folder.with_user(self.manager_a).write({"company_id": self.company_b.id})

    def test_company_immutability_by_admin(self):
        folder = self._create_folder()
        with self.assertRaises(ValidationError):
            folder.with_user(self.admin_a).write({"company_id": self.company_b.id})

    def test_multi_record_write_denied(self):
        folder_assigned = self._create_folder(collaborator_ids=[Command.set([self.user_a.id])], code="ASSIGNED")
        folder_unassigned = self._create_folder(code="UNASSIGNED")
        with self.assertRaises(AccessError):
            self.env["ca.accounting.folder"].with_user(self.user_a).browse(
                [folder_assigned.id, folder_unassigned.id]
            ).write({"description": "bulk"})

    def test_manager_cross_company_denied(self):
        folder_b = self._create_folder(company=self.company_b, manager=self.user_b, code="B-FOLDER")
        with self.assertRaises(AccessError):
            folder_b.with_user(self.manager_a).read(["name"])

    def test_manager_rights(self):
        folder = self._create_folder()
        self.assertTrue(folder.with_user(self.manager_a).has_access("write"))

    def test_admin_rights(self):
        folder = self._create_folder()
        self.assertTrue(folder.with_user(self.admin_a).has_access("write"))

    def test_admin_can_modify_archived_folder(self):
        folder = self._create_folder()
        folder.action_activate()
        folder.action_close()
        folder.action_archive()
        folder.with_user(self.admin_a).write({"description": "admin change"})
        self.assertEqual(folder.description, "admin change")

    def test_collaborator_unauthorized_add(self):
        folder = self._create_folder()
        with self.assertRaises(ValidationError):
            folder.write({"collaborator_ids": [Command.link(self.user_b.id)]})

    def test_user_access_after_company_removed(self):
        user = self.env["res.users"].create(
            {
                "name": "Temporary User",
                "login": "ca_test_temporary",
                "company_id": self.company_a.id,
                "company_ids": [Command.set([self.company_a.id])],
                "group_ids": [Command.set([self.group_user.id])],
            }
        )
        folder = self._create_folder(collaborator_ids=[Command.set([user.id])])
        user.write({"company_ids": [Command.set([self.company_b.id])], "company_id": self.company_b.id})
        with self.assertRaises(AccessError):
            folder.with_user(user).read(["name"])
