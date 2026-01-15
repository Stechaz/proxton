{
    'name': 'Proxton',
    'version': '0.1',
    'summary': 'Proxton',
    'description': 'Proxton',
    'author': 'Strauberi',
    'website': 'https://www.strauberi.com',
    'category': 'Strauberi',
    'depends': ['base', 'crm', 'sale_management', 'stock', 'mrp', 'web_studio', 'project', 'purchase', 'ai_app', 'portal'],
    'data': [
        'security/ir.model.access.csv',
        'security/stock_security.xml',
        'data/proxton_checklist_data.xml',
        'views/crm_lead_views.xml',
        'views/stock_portal_templates.xml',
    ],
}