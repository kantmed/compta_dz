import json
import uuid

from odoo import _, api, fields, models


class CaAuditLog(models.Model):
    _name = "ca.audit.log"
    _description = "Audit Log"
    _order = "date desc, id desc"

    company_id = fields.Many2one("res.company", index=True)
    folder_id = fields.Many2one("ca.accounting.folder", index=True)
    user_id = fields.Many2one("res.users", required=True, default=lambda self: self.env.user, index=True)
    date = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    model_name = fields.Char(required=True, index=True)
    res_id = fields.Integer(index=True)
    record_name = fields.Char()
    operation = fields.Selection(
        [
            ("create", "Create"),
            ("write", "Update"),
            ("unlink", "Delete"),
            ("validate", "Validate"),
            ("cancel", "Cancel"),
            ("archive", "Archive"),
            ("unarchive", "Unarchive"),
            ("change_manager", "Change manager"),
            ("change_folder", "Change folder"),
            ("change_company", "Change company"),
        ],
        required=True,
    )
    old_values = fields.Text()
    new_values = fields.Text()
    description = fields.Text()
    ip_address = fields.Char()
    origin = fields.Char()
    sensitivity = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        default="medium",
        required=True,
    )
    correlation_id = fields.Char(index=True)

    @api.model
    def log(self, operation, records, old_values=None, new_values=None, description=None, sensitivity="medium", correlation_id=None):
        if self.env.context.get("ca_audit_log_disable") or self.env.context.get("install_mode"):
            return
        if not records:
            return
        ip_address, origin, generated_correlation = self._ca_audit_request_info()
        correlation_id = correlation_id or generated_correlation
        for index, record in enumerate(records):
            record_old = None
            record_new = None
            if old_values:
                record_old = old_values[index] if isinstance(old_values, list) else old_values
            if new_values:
                record_new = new_values[index] if isinstance(new_values, list) else new_values

            def company_of(rec):
                if rec._name == "ca.accounting.folder":
                    return rec.company_id.id or False
                if hasattr(rec, "company_id") and rec.company_id:
                    return rec.company_id.id
                if rec._name == "account.move.line" and rec.move_id:
                    return rec.move_id.company_id.id
                if rec._name == "account.payment":
                    return rec.company_id.id if rec.company_id else False
                if rec._name == "ir.attachment" and rec.res_model == "account.move":
                    move = self.env["account.move"].browse(rec.res_id)
                    return move.company_id.id if move else False
                return False

            def folder_of(rec):
                if rec._name == "ca.accounting.folder":
                    return rec.id
                if hasattr(rec, "ca_accounting_folder_id") and rec.ca_accounting_folder_id:
                    return rec.ca_accounting_folder_id.id
                if rec._name == "account.move.line" and rec.move_id:
                    return rec.move_id.ca_accounting_folder_id.id if rec.move_id.ca_accounting_folder_id else False
                if rec._name == "account.payment":
                    return rec.ca_accounting_folder_id.id if rec.ca_accounting_folder_id else False
                if rec._name == "ir.attachment" and rec.res_model == "account.move":
                    move = self.env["account.move"].browse(rec.res_id)
                    return move.ca_accounting_folder_id.id if move and move.ca_accounting_folder_id else False
                return False

            vals = {
                "company_id": company_of(record) or False,
                "folder_id": folder_of(record) or False,
                "user_id": self.env.user.id,
                "date": fields.Datetime.now(),
                "model_name": record._name,
                "res_id": record.id,
                "record_name": record.display_name,
                "operation": operation,
                "old_values": self._ca_audit_serialize(record_old),
                "new_values": self._ca_audit_serialize(record_new),
                "description": (description or f"{operation} on {record._name}"),
                "ip_address": self._ca_audit_request_info()[0],
                "origin": self._ca_audit_request_info()[1],
                "sensitivity": sensitivity,
                "correlation_id": correlation_id,
            }
            self.with_context(ca_audit_log_disable=True).create(vals)

    @api.model
    def _ca_audit_request_info(self):
        ip_address = False
        origin = "server"
        correlation_id = str(uuid.uuid4())
        try:
            from odoo.http import request
            if request and request.httprequest:
                ip_address = request.httprequest.remote_addr
                origin = request.httprequest.path or origin
                if getattr(request, "session", None):
                    correlation_id = request.session.sid or correlation_id
        except Exception:
            pass
        return ip_address, origin, correlation_id

    @api.model
    def _ca_audit_serialize(self, values):
        if values is None:
            return False
        if isinstance(values, (list, tuple)):
            values = values[0] if values and isinstance(values[0], dict) else values
        if isinstance(values, dict):
            sanitized = {}
            for key, value in values.items():
                lower = key.lower()
                if any(term in lower for term in ("password", "token", "secret", "api_key", "apikey")):
                    sanitized[key] = "***"
                else:
                    sanitized[key] = value
            return json.dumps(sanitized, default=str, sort_keys=True)
        return json.dumps(values, default=str)
