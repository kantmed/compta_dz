from odoo import Command
from odoo.exceptions import ValidationError
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCaReferential(TransactionCase):

    def test_installation(self):
        module = self.env["ir.module.module"].search([("name", "=", "ca_referential")])
        self.assertEqual(module.state, "installed")

    def test_create_legal_form(self):
        form = self.env["ca.legal.form"].create(
            {
                "code": "TESTLF",
                "name": "Test Legal Form",
                "name_ar": "شكل قانوني تجريبي",
                "name_en": "Test Legal Form",
            }
        )
        self.assertEqual(form.code, "TESTLF")
        self.assertTrue(form.active)

    def test_duplicate_legal_form_code(self):
        self.env["ca.legal.form"].create({"code": "DUP", "name": "First"})
        with self.assertRaises(Exception):
            self.env["ca.legal.form"].create({"code": "DUP", "name": "Second"})

    def test_legal_form_validity_dates(self):
        with self.assertRaises(ValidationError):
            self.env["ca.legal.form"].create(
                {
                    "code": "BADDATE",
                    "name": "Bad Date",
                    "validity_start": "2026-02-01",
                    "validity_end": "2026-01-01",
                }
            )

    def test_create_activity_category(self):
        category = self.env["ca.activity.category"].create(
            {
                "code": "TESTCAT",
                "name": "Test Category",
                "name_ar": "فئة تجريبية",
                "name_en": "Test Category",
            }
        )
        self.assertEqual(category.code, "TESTCAT")

    def test_duplicate_activity_category_code(self):
        self.env["ca.activity.category"].create({"code": "DUPCAT", "name": "First"})
        with self.assertRaises(Exception):
            self.env["ca.activity.category"].create({"code": "DUPCAT", "name": "Second"})

    def test_activity_category_hierarchy(self):
        parent = self.env["ca.activity.category"].create({"code": "PARENT", "name": "Parent"})
        child = self.env["ca.activity.category"].create({"code": "CHILD", "name": "Child", "parent_id": parent.id})
        self.assertEqual(child.parent_id, parent)
        self.assertIn(child, parent.child_ids)

    def test_recursive_category(self):
        category = self.env["ca.activity.category"].create({"code": "REC", "name": "Recursive"})
        with self.assertRaises(ValidationError):
            category.write({"parent_id": category.id})

    def test_legal_forms_loaded(self):
        forms = self.env["ca.legal.form"].search([])
        self.assertGreaterEqual(len(forms), 9)

    def test_activity_categories_loaded(self):
        categories = self.env["ca.activity.category"].search([])
        self.assertGreaterEqual(len(categories), 6)

    def test_legal_form_inactive(self):
        form = self.env["ca.legal.form"].create({"code": "INACTIVE", "name": "Inactive", "active": False})
        self.assertFalse(form.active)

    def test_activity_category_inactive(self):
        category = self.env["ca.activity.category"].create({"code": "INACTIVECAT", "name": "Inactive", "active": False})
        self.assertFalse(category.active)


from odoo import Command


@tagged("post_install", "-at_install")
class TestCaReferentialSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_user = cls.env.ref("ca_core.group_ca_core_user")
        cls.group_manager = cls.env.ref("ca_core.group_ca_core_manager")
        cls.group_admin = cls.env.ref("ca_core.group_ca_core_admin")
        cls.audit_admin = cls.env.ref("ca_audit_log.group_ca_audit_log_admin")
        cls.env.user.write({"group_ids": [(4, cls.audit_admin.id)]})

        cls.ordinary_user = cls.env["res.users"].create(
            {
                "name": "Referential User",
                "login": "ca_ref_user",
                "group_ids": [Command.set([cls.group_user.id])],
            }
        )
        cls.manager_user = cls.env["res.users"].create(
            {
                "name": "Referential Manager",
                "login": "ca_ref_manager",
                "group_ids": [Command.set([cls.group_manager.id])],
            }
        )
        cls.admin_user = cls.env["res.users"].create(
            {
                "name": "Referential Admin",
                "login": "ca_ref_admin",
                "group_ids": [Command.set([cls.group_admin.id])],
            }
        )

    def test_user_cannot_create_legal_form(self):
        with self.assertRaises(AccessError):
            self.env["ca.legal.form"].with_user(self.ordinary_user).create({"code": "U1", "name": "User Form"})

    def test_user_cannot_write_legal_form(self):
        form = self.env["ca.legal.form"].create({"code": "W1", "name": "Writable"})
        with self.assertRaises(AccessError):
            form.with_user(self.ordinary_user).write({"name": "Changed"})

    def test_user_cannot_unlink_legal_form(self):
        form = self.env["ca.legal.form"].create({"code": "D1", "name": "Deletable"})
        with self.assertRaises(AccessError):
            form.with_user(self.ordinary_user).unlink()

    def test_manager_can_create_legal_form(self):
        form = self.env["ca.legal.form"].with_user(self.manager_user).create({"code": "M1", "name": "Manager Form"})
        self.assertEqual(form.code, "M1")

    def test_admin_can_create_legal_form(self):
        form = self.env["ca.legal.form"].with_user(self.admin_user).create({"code": "A1", "name": "Admin Form"})
        self.assertEqual(form.code, "A1")

    def test_audit_log_created_on_legal_form_create(self):
        before = self.env["ca.audit.log"].search_count([])
        self.env["ca.legal.form"].create({"code": "AUDITLF", "name": "Audit Legal Form"})
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)

    def test_audit_log_created_on_legal_form_write(self):
        form = self.env["ca.legal.form"].create({"code": "AUDITLF2", "name": "Audit Legal Form 2"})
        before = self.env["ca.audit.log"].search_count([])
        form.write({"name": "Changed Name"})
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)

    def test_audit_log_created_on_legal_form_unlink(self):
        form = self.env["ca.legal.form"].create({"code": "AUDITLF3", "name": "Audit Legal Form 3"})
        before = self.env["ca.audit.log"].search_count([])
        form.unlink()
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)
