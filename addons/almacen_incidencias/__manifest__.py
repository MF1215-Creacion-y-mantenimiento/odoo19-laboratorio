# almacen_incidencias/__manifest__.py
{
    'name': 'Incidencias de almacén',
    'version': '19.0.1.0.0',
    'summary': 'Registro y seguimiento de roturas, caducidades y otras incidencias de mercancías',
    'category': 'Inventory/Inventory',
    'author': 'Rafael Martín',
    'license': 'LGPL-3',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/secuencia.xml',
        'views/incidencia_views.xml',
        'views/menus.xml',
    ],
    'application': True,
    'installable': True,
}