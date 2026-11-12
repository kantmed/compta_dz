from odoo import api, fields, models


class CaCollaborationDashboard(models.TransientModel):
    _name = "ca.collaboration.dashboard"
    _description = "Collaboration Dashboard"

    active_collaboration_count = fields.Integer(compute="_compute_kpis", readonly=True)
    todo_task_count = fields.Integer(compute="_compute_kpis", readonly=True)
    overdue_task_count = fields.Integer(compute="_compute_kpis", readonly=True)
    urgent_task_count = fields.Integer(compute="_compute_kpis", readonly=True)
    pending_request_count = fields.Integer(compute="_compute_kpis", readonly=True)
    received_request_count = fields.Integer(compute="_compute_kpis", readonly=True)
    unread_message_count = fields.Integer(compute="_compute_kpis", readonly=True)

    def _compute_kpis(self):
        for dashboard in self:
            collaborations = self.env["ca.collaboration"].search([("state", "=", "active")])
            tasks = self.env["ca.collaboration.task"].search([("state", "not in", ("done", "cancelled"))])
            requests = self.env["ca.collaboration.document.request"].search([])
            messages = self.env["ca.collaboration.message"].search([("is_read", "=", False)])
            dashboard.active_collaboration_count = len(collaborations)
            dashboard.todo_task_count = len(tasks.filtered(lambda t: t.state in ("new", "todo")))
            dashboard.overdue_task_count = len(tasks.filtered(lambda t: t.date_deadline and t.date_deadline < fields.Date.today()))
            dashboard.urgent_task_count = len(tasks.filtered(lambda t: t.priority == "urgent"))
            dashboard.pending_request_count = len(requests.filtered(lambda r: r.state in ("sent", "in_progress")))
            dashboard.received_request_count = len(requests.filtered(lambda r: r.state == "received"))
            dashboard.unread_message_count = len(messages)
