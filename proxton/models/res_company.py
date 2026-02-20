from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    tax_id = fields.Char(related='partner_id.tax_id')

    work_entry_rounding_interval = fields.Integer(
        string='Work Entry Rounding Interval',
        default=0,
        help='Round work entry duration to the nearest X minutes. '
             'Set to 0 to disable rounding. '
             'Example: 15 means round to nearest 15 minutes (8:07 -> 8:00, 8:08 -> 8:15)',
    )
