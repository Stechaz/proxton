from odoo import api, fields, models


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'portal.mixin']

    def _compute_access_url(self):
        super()._compute_access_url()
        for picking in self:
            picking.access_url = f'/my/deliveries/{picking.id}'

    def _get_report_base_filename(self):
        self.ensure_one()
        return f'Delivery-{self.name}'

    def get_portal_url(self, suffix=None, report_type=None, download=None, query_string=None):
        """Get the portal URL for this delivery slip."""
        self.ensure_one()
        url = self.access_url
        if suffix:
            url += suffix
        if report_type or download or query_string:
            url += '?'
            params = []
            if report_type:
                params.append(f'report_type={report_type}')
            if download:
                params.append('download=true')
            if query_string:
                params.append(query_string)
            url += '&'.join(params)
        return url

