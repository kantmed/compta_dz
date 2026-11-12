from odoo import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCaAccountingFolderAccounting(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.folder = cls.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Folder A",
                "code": "FOLDER-A",
                "company_id": cls.env.company.id,
                "manager_id": cls.env.user.id,
            }
        )
        cls.other_company = cls.setup_other_company()
        cls.other_folder = cls.env["ca.accounting.folder"].sudo().with_company(cls.other_company["company"]).create(
            {
                "name": "Folder B",
                "code": "FOLDER-B",
                "company_id": cls.other_company["company"].id,
                "manager_id": cls.env.user.id,
            }
        )

        cls.group_user = cls.env.ref("ca_core.group_ca_core_user")
        cls.group_manager = cls.env.ref("ca_core.group_ca_core_manager")
        cls.group_admin = cls.env.ref("ca_core.group_ca_core_admin")

        cls.collaborator = cls.env["res.users"].create(
            {
                "name": "Collaborator",
                "login": "ca_folder_collaborator",
                "company_id": cls.env.company.id,
                "company_ids": [Command.set([cls.env.company.id])],
                "group_ids": [Command.set([cls.group_user.id, cls.env.ref("account.group_account_user").id])],
            }
        )
        cls.folder.write({"collaborator_ids": [Command.link(cls.collaborator.id)]})

        cls.manager_user = cls.env["res.users"].create(
            {
                "name": "Folder Manager",
                "login": "ca_folder_manager",
                "company_id": cls.env.company.id,
                "company_ids": [Command.set([cls.env.company.id])],
                "group_ids": [Command.set([cls.group_manager.id, cls.env.ref("account.group_account_user").id])],
            }
        )
        cls.admin_user = cls.env["res.users"].create(
            {
                "name": "Folder Admin",
                "login": "ca_folder_admin",
                "company_id": cls.env.company.id,
                "company_ids": [Command.set([cls.env.company.id])],
                "group_ids": [Command.set([cls.group_admin.id, cls.env.ref("account.group_account_user").id])],
            }
        )

    def test_installation(self):
        module = self.env["ir.module.module"].search([("name", "=", "ca_accounting_folder")])
        self.assertEqual(module.state, "installed")

    def test_invoice_with_folder(self):
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_sale"].id,
                "ca_accounting_folder_id": self.folder.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        self.assertEqual(move.ca_accounting_folder_id, self.folder)
        self.assertTrue(all(line.ca_accounting_folder_id == self.folder for line in move.line_ids))

    def test_entry_with_folder(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": self.folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        self.assertEqual(move.ca_accounting_folder_id, self.folder)

    def test_incompatible_company_folder(self):
        with self.assertRaises(ValidationError):
            self.env["account.move"].create(
                {
                    "move_type": "entry",
                    "date": "2026-01-01",
                    "journal_id": self.company_data["default_journal_misc"].id,
                    "company_id": self.env.company.id,
                    "ca_accounting_folder_id": self.other_folder.id,
                    "line_ids": [
                        Command.create(
                            {
                                "name": "debit",
                                "account_id": self.company_data["default_account_revenue"].id,
                                "debit": 100.0,
                                "credit": 0.0,
                            }
                        ),
                        Command.create(
                            {
                                "name": "credit",
                                "account_id": self.company_data["default_account_expense"].id,
                                "debit": 0.0,
                                "credit": 100.0,
                            }
                        ),
                    ],
                }
            )

    def test_change_folder_before_posting(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": self.folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        new_folder = self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Folder 2",
                "code": "FOLDER-2",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        move.write({"ca_accounting_folder_id": new_folder.id})
        self.assertEqual(move.ca_accounting_folder_id, new_folder)

    def test_change_folder_after_posting(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": self.folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        move.action_post()
        with self.assertRaises(ValidationError):
            move.write({"ca_accounting_folder_id": False})

    def test_move_lines_folder(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": self.folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        self.assertTrue(all(line.ca_accounting_folder_id == self.folder for line in move.line_ids))

    def test_payment_client(self):
        move = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_sale"].id,
                "ca_accounting_folder_id": self.folder.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        move.action_post()
        wizard = self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=move.ids
        ).create({"amount": 100.0})
        payment = wizard._create_payments()
        self.assertEqual(payment.ca_accounting_folder_id, move.ca_accounting_folder_id)

    def test_payment_supplier(self):
        move = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "invoice_date": "2026-01-01",
                "date": "2026-01-01",
                "partner_id": self.partner_a.id,
                "journal_id": self.company_data["default_journal_purchase"].id,
                "ca_accounting_folder_id": self.folder.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_a.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        move.action_post()
        wizard = self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=move.ids
        ).create({"amount": 100.0})
        payment = wizard._create_payments()
        self.assertEqual(payment.ca_accounting_folder_id, move.ca_accounting_folder_id)

    def test_isolation_between_folders(self):
        folder2 = self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Folder 2",
                "code": "FOLDER-2",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": folder2.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        self.assertTrue(move.with_user(self.collaborator).search_count([("id", "=", move.id)]) == 0)

    def test_isolation_between_companies(self):
        other_move = self.env["account.move"].with_company(self.other_company["company"]).create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.other_company["default_journal_misc"].id,
                "ca_accounting_folder_id": self.other_folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.other_company["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.other_company["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        self.assertTrue(self.env["account.move"].with_user(self.collaborator).search_count([("id", "=", other_move.id)]) == 0)

    def test_collaborator_access(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": self.folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        self.assertEqual(move.with_user(self.collaborator).ca_accounting_folder_id, self.folder)

    def test_manager_access(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": self.folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        self.assertEqual(move.with_user(self.manager_user).ca_accounting_folder_id, self.folder)

    def test_admin_access(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": self.folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        self.assertEqual(move.with_user(self.admin_user).ca_accounting_folder_id, self.folder)

    def test_search_and_filter(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": self.folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        count = self.env["account.move"].search_count([("ca_accounting_folder_id", "=", self.folder.id)])
        self.assertGreaterEqual(count, 1)

    def test_payment_internal(self):
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_id": self.partner_a.id,
                "amount": 50.0,
                "journal_id": self.company_data["default_journal_bank"].id,
                "payment_method_line_id": self.company_data["default_journal_bank"].outbound_payment_method_line_ids[:1].id,
            }
        )
        self.assertFalse(payment.ca_accounting_folder_id)

    def test_reconciliation(self):
        move1 = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": self.folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "receivable",
                            "account_id": self.company_data["default_account_receivable"].id,
                            "partner_id": self.partner_a.id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "revenue",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        move2 = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-02",
                "journal_id": self.company_data["default_journal_misc"].id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "bank",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "receivable",
                            "account_id": self.company_data["default_account_receivable"].id,
                            "partner_id": self.partner_a.id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        move1.action_post()
        move2.action_post()
        lines = (move1.line_ids + move2.line_ids).filtered(
            lambda line: line.account_id == self.company_data["default_account_receivable"]
        )
        lines.reconcile()
        self.assertEqual(move1.ca_accounting_folder_id, self.folder)

    def test_access_move_lines(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": self.folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        line = move.line_ids[:1]
        self.assertEqual(line.with_user(self.collaborator).ca_accounting_folder_id, self.folder)
        other_folder = self.env["ca.accounting.folder"].sudo().create(
            {
                "name": "Other Folder",
                "code": "OTHER-FOLDER",
                "company_id": self.env.company.id,
                "manager_id": self.env.user.id,
            }
        )
        other_move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": other_folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        other_line = other_move.line_ids[:1]
        with self.assertRaises(AccessError):
            other_line.with_user(self.collaborator).read(["name"])

    def test_module_installed(self):
        module = self.env["ir.module.module"].search([("name", "=", "ca_accounting_folder")])
        self.assertEqual(module.state, "installed")

    def test_attachment_access(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "journal_id": self.company_data["default_journal_misc"].id,
                "ca_accounting_folder_id": self.folder.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "debit",
                            "account_id": self.company_data["default_account_revenue"].id,
                            "debit": 100.0,
                            "credit": 0.0,
                        }
                    ),
                    Command.create(
                        {
                            "name": "credit",
                            "account_id": self.company_data["default_account_expense"].id,
                            "debit": 0.0,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        attachment = self.env["ir.attachment"].create(
            {
                "name": "test.txt",
                "raw": b"test",
                "res_model": "account.move",
                "res_id": move.id,
            }
        )
        self.assertEqual(attachment.ca_accounting_folder_id, self.folder)
        self.assertEqual(attachment.with_user(self.collaborator).ca_accounting_folder_id, self.folder)
