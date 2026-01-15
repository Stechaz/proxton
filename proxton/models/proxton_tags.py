from odoo import fields, models


class ProxtonEnvironmentTag(models.Model):
    _name = 'proxton.environment.tag'
    _description = 'Environment Tag'

    name = fields.Char(string='Name', required=True, translate=True)
    color = fields.Integer(string='Color')
    active = fields.Boolean(default=True)


class ProxtonIndustryTag(models.Model):
    _name = 'proxton.industry.tag'
    _description = 'Industry Tag'

    name = fields.Char(string='Name', required=True, translate=True)
    color = fields.Integer(string='Color')
    active = fields.Boolean(default=True)
