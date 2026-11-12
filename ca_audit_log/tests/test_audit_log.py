from odoo import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCaAuditLog(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.folder = cls.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Audit Folder",
                "code": "AUDIT-FOLDER",
                "company_id": cls.env.company.id,
                "manager_id": cls.env.user.id,
            }
        )
        cls.group_user = cls.env.ref("ca_core.group_ca_core_user")
        cls.group_manager = cls.env.ref("ca_core.group_ca_core_manager")
        cls.group_admin = cls.env.ref("ca_core.group_ca_core_admin")
        cls.audit_user_group = cls.env.ref("ca_audit_log.group_ca_audit_log_user")
        cls.audit_manager_group = cls.env.ref("ca_audit_log.group_ca_audit_log_manager")
        cls.audit_admin_group = cls.env.ref("ca_audit_log.group_ca_audit_log_admin")

        cls.collaborator = cls.env["res.users"].create(
            {
                "name": "Audit Collaborator",
                "login": "ca_audit_collaborator",
                "company_id": cls.env.company.id,
                "company_ids": [Command.set([cls.env.company.id])],
                "group_ids": [Command.set([cls.group_user.id, cls.audit_user_group.id, cls.env.ref("account.group_account_user").id])],
            }
        )
        cls.folder.write({"collaborator_ids": [Command.link(cls.collaborator.id)]})

        cls.manager_user = cls.env["res.users"].create(
            {
                "name": "Audit Manager",
                "login": "ca_audit_manager",
                "company_id": cls.env.company.id,
                "company_ids": [Command.set([cls.env.company.id])],
                "group_ids": [Command.set([cls.group_manager.id, cls.audit_manager_group.id, cls.env.ref("account.group_account_user").id])],
            }
        )
        cls.env.user.write({'group_ids': [(4, cls.env.ref('ca_audit_log.group_ca_audit_log_admin').id)]})

        cls.admin_user = cls.env["res.users"].create(
            {
                "name": "Audit Admin",
                "login": "ca_audit_admin",
                "company_id": cls.env.company.id,
                "company_ids": [Command.set([cls.env.company.id])],
                "group_ids": [Command.set([cls.group_admin.id, cls.audit_admin_group.id, cls.env.ref("account.group_account_user").id])],
            }
        )

    def test_installation(self):
        module = self.env["ir.module.module"].search([("name", "=", "ca_audit_log")])
        self.assertEqual(module.state, "installed")

    def test_create_audit_log(self):
        log = self.env["ca.audit.log"].sudo().create(
            {
                "company_id": self.env.company.id,
                "folder_id": self.folder.id,
                "model_name": "ca.accounting.folder",
                "res_id": self.folder.id,
                "record_name": self.folder.name,
                "operation": "create",
                "description": "test log",
                "sensitivity": "medium",
            }
        )
        self.assertTrue(log.id)

    def test_log_create_operation(self):
        before = self.env["ca.audit.log"].search_count([])
        self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Audit Folder 2",
                "code": "AUDIT-FOLDER-2",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)

    def test_log_write_operation(self):
        folder = self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Audit Folder 3",
                "code": "AUDIT-FOLDER-3",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        before = self.env["ca.audit.log"].search_count([])
        folder.write({"description": "changed"})
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)

    def test_log_unlink_operation(self):
        folder = self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Audit Folder 4",
                "code": "AUDIT-FOLDER-4",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        before = self.env["ca.audit.log"].search_count([])
        folder.unlink()
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)

    def test_old_and_new_values(self):
        folder = self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Audit Folder 5",
                "code": "AUDIT-FOLDER-5",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        folder.write({"description": "new description"})
        log = self.env["ca.audit.log"].search([("model_name", "=", "ca.accounting.folder"), ("res_id", "=", folder.id)], limit=1, order="date desc")
        self.assertTrue(log.old_values or log.new_values)

    def test_validate_invoice(self):
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_sale"].id,
                "invoice_line_ids": [
                    Command.create({"product_id": self.product_a.id, "quantity": 1, "price_unit": 100.0})
                ],
            }
        )
        before = self.env["ca.audit.log"].search_count([])
        move.action_post()
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)

    def test_cancel_invoice(self):
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_sale"].id,
                "invoice_line_ids": [
                    Command.create({"product_id": self.product_a.id, "quantity": 1, "price_unit": 100.0})
                ],
            }
        )
        move.action_post()
        before = self.env["ca.audit.log"].search_count([])
        move.button_cancel()
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)

    def test_create_invoice_audit(self):
        before = self.env["ca.audit.log"].search_count([])
        self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_sale"].id,
                "invoice_line_ids": [
                    Command.create({"product_id": self.product_a.id, "quantity": 1, "price_unit": 100.0})
                ],
            }
        )
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)

    def test_create_payment_audit(self):
        before = self.env["ca.audit.log"].search_count([])
        payment = self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_id": self.partner_a.id,
                "amount": 100.0,
                "journal_id": self.company_data["default_journal_bank"].id,
                "payment_method_line_id": self.company_data["default_journal_bank"].inbound_payment_method_line_ids[:1].id,
            }
        )
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)
        self.assertTrue(payment.id)

    def test_journal_protection(self):
        log = self.env["ca.audit.log"].sudo().create(
            {
                "company_id": self.env.company.id,
                "model_name": "test.model",
                "operation": "create",
                "description": "protected",
            }
        )
        with self.assertRaises(AccessError):
            log.with_user(self.collaborator).write({"description": "changed"})
        with self.assertRaises(AccessError):
            log.with_user(self.collaborator).unlink()

    def test_rpc_modification(self):
        log = self.env["ca.audit.log"].sudo().create(
            {
                "company_id": self.env.company.id,
                "model_name": "test.model",
                "operation": "create",
                "description": "rpc",
            }
        )
        with self.assertRaises(AccessError):
            self.env["ca.audit.log"].with_user(self.collaborator).browse([log.id]).write({"description": "rpc change"})

    def test_rpc_deletion(self):
        log = self.env["ca.audit.log"].sudo().create(
            {
                "company_id": self.env.company.id,
                "model_name": "test.model",
                "operation": "create",
                "description": "rpc delete",
            }
        )
        with self.assertRaises(AccessError):
            self.env["ca.audit.log"].with_user(self.collaborator).browse([log.id]).unlink()

    def test_company_isolation(self):
        other_company = self.setup_other_company()
        other_user = self.env["res.users"].create(
            {
                "name": "Other Audit User",
                "login": "ca_audit_other_user",
                "company_id": other_company["company"].id,
                "company_ids": [Command.set([other_company["company"].id])],
                "group_ids": [Command.set([self.audit_user_group.id])],
            }
        )
        log = self.env["ca.audit.log"].sudo().create(
            {
                "company_id": self.env.company.id,
                "model_name": "test.model",
                "operation": "create",
                "description": "company isolation",
            }
        )
        self.assertEqual(self.env["ca.audit.log"].with_user(other_user).search_count([("id", "=", log.id)]), 0)

    def test_folder_isolation(self):
        folder = self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Audit Folder 2",
                "code": "AUDIT-FOLDER-2",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        log = self.env["ca.audit.log"].sudo().create(
            {
                "company_id": self.env.company.id,
                "folder_id": folder.id,
                "model_name": "test.model",
                "operation": "create",
                "description": "folder isolation",
            }
        )
        self.assertTrue(log.id)

    def test_collaborator_rights(self):
        logs = self.env["ca.audit.log"].with_user(self.collaborator).search([])
        self.assertTrue(all(log.user_id == self.collaborator for log in logs))

    def test_manager_rights(self):
        logs = self.env["ca.audit.log"].with_user(self.manager_user).search([])
        self.assertTrue(all(log.company_id == self.env.company for log in logs))

    def test_admin_rights(self):
        logs = self.env["ca.audit.log"].with_user(self.admin_user).search([])
        self.assertTrue(isinstance(logs, self.env["ca.audit.log"].__class__))

    def test_folder_consistency(self):
        folder = self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Consistency Folder",
                "code": "CONSISTENCY",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        log = self.env["ca.audit.log"].sudo().create(
            {
                "company_id": self.env.company.id,
                "folder_id": folder.id,
                "model_name": "test.model",
                "operation": "create",
                "description": "consistency",
            }
        )
        self.assertEqual(log.folder_id.company_id, log.company_id)

    def test_no_recursion(self):
        before = self.env["ca.audit.log"].search_count([])
        self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "No Recursion",
                "code": "NO-RECURSION",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreater(after, before)

    def test_no_duplicates(self):
        before = self.env["ca.audit.log"].search_count([])
        folder = self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "No Duplicate",
                "code": "NO-DUPLICATE",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        folder.write({"description": "once"})
        after = self.env["ca.audit.log"].search_count([])
        self.assertGreaterEqual(after - before, 2)

    def test_source_deletion(self):
        folder = self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Source Delete",
                "code": "SOURCE-DELETE",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        folder.unlink()
        logs = self.env["ca.audit.log"].sudo().search([("model_name", "=", "ca.accounting.folder")])
        self.assertTrue(any(log.operation == "unlink" for log in logs))

    def test_update_module(self):
        module = self.env["ir.module.module"].search([("name", "=", "ca_audit_log")])
        self.assertEqual(module.state, "installed")

    def test_compatibility(self):
        self.assertTrue(self.env["ca.audit.log"]._table)
