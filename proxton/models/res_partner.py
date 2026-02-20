from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    tax_id = fields.Char(
        string='DIČ'
    )
