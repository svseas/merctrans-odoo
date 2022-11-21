# -*- coding: utf-8 -*-
{
    "name": "merctrans_projects",
    "summary": """
        To manage MercTrans Localization Projects""",
    "description": """
        To manage MercTrans Localization Projects 
    """,
    "sequence": -100,
    "author": "The Merc",
    "website": "https://merctrans.vn",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "MerctransProject",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "mail"],
    # always loaded
    "data": [
        # Seicurity in order xml -> csv
        "security/security.xml",
        "security/security_rules.xml",
        "security/ir.model.access.csv",
        "data/email_template.xml",
        # View <>
        "views/pos.xml",
        "views/contributors.xml",
        "views/projects_menus.xml",
        "views/clients.xml",
        "views/templates.xml",
        "views/sale.xml",
        "data/automation.xml",
        # data
        "data/currencies.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
