import json
import uuid
from datetime import datetime

from odoo import _, api, fields, models
from odoo.http import request


class CaAuditMixin(models.AbstractModel):
    _name = "ca.audit.mixin"
    _description = "Audit mixin"

    @api.model
    def _ca_audit_disabled(self):
        return bool(self.env.context.get("ca_audit_log_disable") or self.env.context.get("install_mode"))

    @api.model
    def _ca_audit_request_info(self):
        ip_address = False
        origin = "server"
        correlation_id = str(uuid.uuid4())
        try:
            if request and request.httprequest:
                ip_address = request.httprequest.remote_addr
                origin = request.httprequest.path or origin
                if getattr(request, "session", None):
                    correlation_id = request.session.sid or correlation_id
        except Exception:
            pass
        return ip_address, origin, correlation_id

    @api.model
    def _ca_audit_company(self, record):
        if record._name == "ca.accounting.folder":
            return record.company_id.id or False
        if hasattr(record, "company_id") and record.company_id:
            return record.company_id.id
        if record._name == "account.move.line" and record.move_id:
            return record.move_id.company_id.id
        if record._name == "account.payment":
            return record.company_id.id if record.company_id else False
        if record._name == "ir.attachment" and record.res_model == "account.move":
            move = self.env["account.move"].sudo().browse(record.res_id)
            return move.company_id.id if move else False
        return False

    @api.model
    def _ca_audit_folder(self, record):
        if record._name == "ca.accounting.folder":
            return record.id
        if hasattr(record, "ca_accounting_folder_id") and record.ca_accounting_folder_id:
            return record.ca_accounting_folder_id.id
        if record._name == "account.move.line" and record.move_id:
            return record.move_id.ca_accounting_folder_id.id if record.move_id.ca_accounting_folder_id else False
        if record._name == "account.payment":
            return record.ca_accounting_folder_id.id if record.ca_accounting_folder_id else False
        if record._name == "ir.attachment" and record.res_model == "account.move":
            move = self.env["account.move"].sudo().browse(record.res_id)
            return move.ca_accounting_folder_id.id if move and move.ca_accounting_folder_id else False
        return False

    @api.model
    def _ca_audit_sanitize(self, values):
        if not values:
            return values
        result = {}
        for key, value in values.items():
            lower = key.lower()
            if any(term in lower for term in ("password", "token", "secret", "api_key", "apikey")):
                result[key] = "***"
            else:
                result[key] = value
        return result

    @api.model
    def _ca_audit_serialize(self, values):
        if values is None:
            return False
        if isinstance(values, (list, tuple)):
            values = values[0] if values and isinstance(values[0], dict) else values
        if isinstance(values, dict):
            return json.dumps(self._ca_audit_sanitize(values), default=str, sort_keys=True)
        return json.dumps(values, default=str)

    @api.model
    def _ca_audit_excluded_fields(self):
        return {
            "id",
            "create_uid",
            "create_date",
            "write_uid",
            "write_date",
            "display_name",
            "password",
            "new_password",
            "password_crypt",
            "token",
            "secret",
            "api_key",
            "apikey",
            "access_token",
            "refresh_token",
            "raw",
            "db_datas",
            "store_fname",
            "checksum",
        }

    @api.model
    def _ca_audit_tracked_fields(self, record, vals):
        excluded = self._ca_audit_excluded_fields()
        if vals:
            return sorted({
                field for field in vals
                if field in record._fields
                and record._fields[field].store
                and record._fields[field].type != "binary"
                and field not in excluded
            })
        return sorted(
            field for field, field_def in record._fields.items()
            if field_def.store
            and field_def.type != "binary"
            and not field.startswith("_")
            and field not in excluded
        )

    @api.model
    def _ca_audit_sensitivity(self, operation, vals):
        if operation in ("validate", "cancel", "change_company"):
            return "high"
        if operation == "delete":
            return "high"
        if operation in ("change_manager", "change_folder"):
            return "high"
        if self._name in ("account.move", "account.payment") and operation in ("create", "write", "validate", "cancel"):
            return "high"
        if "active" in vals and not vals.get("active"):
            return "medium"
        return "medium"

    @api.model
    def _ca_audit_operation(self, vals, old_states=None):
        if "state" in vals:
            new_state = vals.get("state")
            if new_state == "posted":
                return "validate"
            if new_state == "cancel":
                return "cancel"
            if new_state == "archived":
                return "archive"
            if old_states and any(state == "archived" for state in old_states) and new_state != "archived":
                return "unarchive"
        if "active" in vals:
            if vals.get("active") is False:
                return "archive"
            if vals.get("active") is True and old_states and any(state is False for state in old_states):
                return "unarchive"
        if "manager_id" in vals:
            return "change_manager"
        if "ca_accounting_folder_id" in vals:
            return "change_folder"
        if "company_id" in vals:
            return "change_company"
        return "write"

    @api.model
    def _ca_audit_log(self, operation, records, old_values=None, new_values=None, description=None, sensitivity=None):
        if self._ca_audit_disabled():
            return
        if not records:
            return
        audit_model = self.env["ca.audit.log"]
        ip_address, origin, correlation_id = audit_model._ca_audit_request_info()
        sensitivity = sensitivity or self._ca_audit_sensitivity(operation, {})
        for index, record in enumerate(records):
            record_old = None
            record_new = None
            if old_values:
                record_old = old_values[index] if isinstance(old_values, list) else old_values
            if new_values:
                record_new = new_values[index] if isinstance(new_values, list) else new_values
            vals = {
                "company_id": self._ca_audit_company(record) or False,
                "folder_id": self._ca_audit_folder(record) or False,
                "user_id": self.env.user.id,
                "date": fields.Datetime.now(),
                "model_name": record._name,
                "res_id": record.id,
                "record_name": record.display_name,
                "operation": operation,
                "old_values": audit_model._ca_audit_serialize(record_old),
                "new_values": audit_model._ca_audit_serialize(record_new),
                "description": description or f"{operation} on {record._name}",
                "ip_address": ip_address,
                "origin": origin,
                "sensitivity": sensitivity,
                "correlation_id": correlation_id,
            }
            audit_model.sudo().with_context(ca_audit_log_disable=True).create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        if self._ca_audit_disabled():
            return super().create(vals_list)
        records = super().create(vals_list)
        if self._name == "ca.audit.log":
            return records
        tracked = sorted({field for vals in vals_list for field in vals if field in self._fields and self._fields[field].store})
        new_values = [record.read(tracked) for record in records]
        operation = "create"
        if any(vals.get("state") == "posted" for vals in vals_list):
            operation = "validate"
        sensitivity = self._ca_audit_sensitivity(operation, {})
        self._ca_audit_log(operation, records, new_values=new_values, description=f"{operation} on {self._name}", sensitivity=sensitivity)
        return records

    def write(self, vals):
        if self._ca_audit_disabled() or self._name == "ca.audit.log":
            return super().write(vals)
        tracked = self._ca_audit_tracked_fields(self, vals)
        old_values = [record.read(tracked) for record in self]
        result = super().write(vals)
        new_values = [record.read(tracked) for record in self]
        operation = self._ca_audit_operation(vals, [record.state if "state" in record._fields else None for record in self])
        sensitivity = self._ca_audit_sensitivity(operation, vals)
        description = f"{operation} on {self._name}"
        self._ca_audit_log(operation, self, old_values=old_values, new_values=new_values, description=description, sensitivity=sensitivity)
        return result

    def unlink(self):
        if self._ca_audit_disabled() or self._name == "ca.audit.log":
            return super().unlink()
        tracked = self._ca_audit_tracked_fields(self, {})
        old_values = [record.read(tracked) for record in self]
        record_names = [record.display_name for record in self]
        record_companies = [self._ca_audit_company(record) for record in self]
        record_folders = [self._ca_audit_folder(record) for record in self]
        record_ids = [record.id for record in self]
        result = super().unlink()
        ip_address, origin, correlation_id = self.env["ca.audit.log"]._ca_audit_request_info()
        for index, record_name in enumerate(record_names):
            vals = {
                "company_id": record_companies[index] or False,
                "folder_id": False,
                "user_id": self.env.user.id,
                "date": fields.Datetime.now(),
                "model_name": self._name,
                "res_id": record_ids[index],
                "record_name": record_name,
                "operation": "unlink",
                "old_values": self.env["ca.audit.log"]._ca_audit_serialize(old_values[index] if old_values else None),
                "new_values": False,
                "description": f"delete on {self._name}",
                "ip_address": ip_address,
                "origin": origin,
                "sensitivity": "high",
                "correlation_id": correlation_id,
            }
            self.env["ca.audit.log"].sudo().with_context(ca_audit_log_disable=True).create(vals)
        return result
