from odoo import api, fields, models


class HrWorkEntry(models.Model):
    _inherit = 'hr.work.entry'

    duration_rounded = fields.Float(
        string='Zaokrúhlené hodiny',
        compute='_compute_duration_rounded',
        store=True,
        help='Hodiny zaokrúhlené na najbližší interval definovaný v nastaveniach',
    )

    @api.depends('duration', 'company_id.work_entry_rounding_interval')
    def _compute_duration_rounded(self):
        for entry in self:
            interval = entry.company_id.work_entry_rounding_interval or 0
            if interval > 0:
                # Convert interval from minutes to hours
                interval_hours = interval / 60.0
                # Round to nearest interval
                # e.g., for 15 min interval: 8:07 (8.1167h) -> 8:00 (8h), 8:08 (8.1333h) -> 8:15 (8.25h)
                entry.duration_rounded = round(entry.duration / interval_hours) * interval_hours
            else:
                entry.duration_rounded = entry.duration
