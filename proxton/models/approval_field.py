from odoo import api, fields, models


class ApprovalField(models.Model):
    _name = 'approval.field'
    _description = 'Field Approval'
    _order = 'approval_date desc'
    _rec_name = 'field_name'

    model_name = fields.Char(string='Model', required=True, index=True)
    res_id = fields.Integer(string='Record ID', required=True, index=True)
    field_name = fields.Char(string='Field Name', required=True, index=True)
    approved_value = fields.Text(string='Approved Value')
    approval_date = fields.Datetime(string='Approval Date', default=fields.Datetime.now, required=True)
    approved_by = fields.Many2one('res.users', string='Approved By', default=lambda self: self.env.user, required=True)
    note = fields.Text(string='Note')

    _sql_constraints = [
        ('unique_approval', 'unique(model_name, res_id, field_name)',
         'Only one active approval per field per record is allowed.')
    ]

    @staticmethod
    def _normalize_value(value):
        """Normalize value for consistent storage and comparison.

        Handles lists (Many2many), dicts, and other types.
        """
        if value is None:
            return ''
        if isinstance(value, (list, tuple)):
            # Sort list for consistent comparison (Many2many fields)
            try:
                return str(sorted(value))
            except TypeError:
                return str(list(value))
        return str(value)

    @api.model
    def approve_field(self, model_name, res_id, field_name, value, note=False):
        """Approve a field value. Updates existing approval or creates new one."""
        existing = self.search([
            ('model_name', '=', model_name),
            ('res_id', '=', res_id),
            ('field_name', '=', field_name),
        ], limit=1)

        # Normalize value for consistent storage
        approved_value = self._normalize_value(value)

        vals = {
            'approved_value': approved_value,
            'approval_date': fields.Datetime.now(),
            'approved_by': self.env.user.id,
            'note': note,
        }

        if existing:
            existing.write(vals)
            return existing
        else:
            vals.update({
                'model_name': model_name,
                'res_id': res_id,
                'field_name': field_name,
            })
            return self.create(vals)

    @api.model
    def get_approval_info(self, model_name, res_id, field_name, current_value):
        """Get approval status for a field."""
        approval = self.search([
            ('model_name', '=', model_name),
            ('res_id', '=', res_id),
            ('field_name', '=', field_name),
        ], limit=1)

        if not approval:
            return {
                'is_approved': False,
                'needs_reapproval': False,
                'approval_date': False,
                'approved_by': False,
                'approved_by_name': False,
            }

        # Normalize current value for comparison
        current_str = self._normalize_value(current_value)
        needs_reapproval = current_str != approval.approved_value

        return {
            'is_approved': True,
            'needs_reapproval': needs_reapproval,
            'approval_date': approval.approval_date,
            'approved_by': approval.approved_by.id,
            'approved_by_name': approval.approved_by.name,
        }

    @api.model
    def get_approval_history(self, model_name, res_id, field_name=False):
        """Get approval history for a record, optionally filtered by field."""
        domain = [
            ('model_name', '=', model_name),
            ('res_id', '=', res_id),
        ]
        if field_name:
            domain.append(('field_name', '=', field_name))

        approvals = self.search(domain)
        return [{
            'id': a.id,
            'field_name': a.field_name,
            'approval_date': a.approval_date,
            'approved_by': a.approved_by.id,
            'approved_by_name': a.approved_by.name,
            'note': a.note,
        } for a in approvals]
