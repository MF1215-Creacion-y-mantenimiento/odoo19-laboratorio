# cabeceras de la clase
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class AlmacenIncidencia(models.Model):
    """ Incidencias detectada sobre la mercancía del almacén."""

    _name = 'almacen.incidencia'
    _description = 'Incidencia de almacén'
    _order = 'fecha desc, id desc'

    # campos básicos
    name = fields.Char(
        string='Referencia', required=True, copy=False,
        readonly=True, default='Nuevo',
    )

    fecha = fields.Date(
        string='Fecha', required=True,
        deafault=fields.Date.context_today,
    )

    tipo = fields.Selection(
        selection=[
            ('rotura', 'Rotura o daño'),
            ('caducidad', 'Producto caducado'),
            ('extravio', 'Extravío'),
            ('error_inventario', 'Error de inventario'),
        ],
        string='Tipo', required=True, default='rotura',

    )

    descripcion = fields.Text(string='Descripción')

    # relaciones con otros modelos
    product_id = fields.Many2one(
        comodel_name='product.product', string='Producto',
        required=True, ondelete='restrict',
    )
    uom_id = fields.Many2one(related='product_id.uom_id', string='Unidad')
    location_id = fields.Many2one(
        comodel_name='stock.location', string='Ubicación',
        domain="[('usage', '=', 'internal')]",
    )
    responsable_id = fields.Many2one(
        comodel_name='res.user', string='Responsable',
        default=lambda self: self.env.user,
    )
    company_id = fields.Many2one(
        comodel_name='res.company', string='Compañia',
        required=True, default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(related='company_id.currency_id')
    
    # cantidad, coste calculado y estado
    cantidad = fields.float(string='Cantidad afectada', required=True, defautl=1.0)
    coste_total = fields.Monetary(
        string='Coste estimado', currency_field='currency_id',
        compute='_compute_coste_total', store=True,    
    )
    
    state = fields.Selection(
        selection=[
            ('borrador', 'Borrador'),
            ('confirmada', 'Confirmada'),
            ('resuelta', 'Resuelta'),
            ('cancelada', 'Cancelada')    
        ],
        string='Estado', required=True, default='borrador', copy=False
    )
    
    # Cálculo del coste
    @api.depends('cantidad', 'product_id')
    def _compute_coste_total(self):
        for incidencia in self:
            incidencia.coste_total = incidencia.cantidad * incidencia.product_id.standard_price
            
    # Validaciones
    # Restrición en PostgreSQL(novedad en Odoo 19: models.Constraint)
    
    _cantidad_positiva = models.Constraint(
        'CHECK(cantidad > 0)',
        'La cantida afectada debe ser mayor que cero',

    )
    
    # Validación en Python
    @api.constraint('fecha')
    def _check_fecha(self):
        hoy = fields.Date.context_today(self)
        for incidencia in self:
            if incidencia.fecha > hoy:
                raise ValidationError('La fecha de la incidencia no puede sert futura')
            

    # Referencia automática y borrado controlado
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('almacen.incidencia') or 'Nuevo'
        
        return super().create(vals_list)
    
    @api.ondelete(at_uninstall=False)
    def _unlink_solo_borrador(self):
        if any(incidencia.state != 'borrador' for incidencia in self):
            raise UserError('Solo se pueden eliminar incidencias en estado borrador.')