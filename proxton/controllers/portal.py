from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class DeliveryPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        StockPicking = request.env['stock.picking']
        if 'delivery_count' in counters:
            values['delivery_count'] = StockPicking.search_count(self._prepare_deliveries_domain(partner)) \
                if StockPicking.has_access('read') else 0

        return values

    def _prepare_deliveries_domain(self, partner):
        """Domain for deliveries visible in portal."""
        return [
            ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            ('picking_type_id.code', '=', 'outgoing'),
            ('state', '=', 'done'),
        ]

    def _get_delivery_searchbar_sortings(self):
        return {
            'date': {'label': _('Date'), 'order': 'date_done desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'scheduled': {'label': _('Scheduled Date'), 'order': 'scheduled_date desc'},
        }

    @http.route(['/my/deliveries', '/my/deliveries/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_deliveries(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        StockPicking = request.env['stock.picking']

        domain = self._prepare_deliveries_domain(partner)

        searchbar_sortings = self._get_delivery_searchbar_sortings()
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('date_done', '>', date_begin), ('date_done', '<=', date_end)]

        # Count for pager
        delivery_count = StockPicking.search_count(domain)

        # Pager
        pager = portal_pager(
            url="/my/deliveries",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=delivery_count,
            page=page,
            step=self._items_per_page
        )

        # Content according to pager
        deliveries = StockPicking.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'date': date_begin,
            'deliveries': deliveries.sudo(),
            'page_name': 'delivery',
            'pager': pager,
            'default_url': '/my/deliveries',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("proxton.portal_my_deliveries", values)

    @http.route(['/my/deliveries/<int:picking_id>'], type='http', auth="public", website=True)
    def portal_my_delivery_detail(self, picking_id, access_token=None, report_type=None, download=False, **kw):
        try:
            picking_sudo = self._document_check_access('stock.picking', picking_id, access_token=access_token)
        except Exception:
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=picking_sudo, report_type=report_type, report_ref='stock.action_report_delivery', download=download)

        values = self._delivery_get_page_view_values(picking_sudo, access_token, **kw)
        return request.render("proxton.portal_my_delivery_detail", values)

    def _delivery_get_page_view_values(self, picking, access_token, **kwargs):
        values = {
            'picking': picking,
            'page_name': 'delivery',
            'report_type': 'html',
        }
        return self._get_page_view_values(picking, access_token, values, 'my_deliveries_history', False, **kwargs)

