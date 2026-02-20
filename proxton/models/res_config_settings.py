from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    work_entry_rounding_interval = fields.Integer(
        related='company_id.work_entry_rounding_interval',
        readonly=False,
        string='Zaokrúhlenie pracovného času (minúty)',
    )
