from odoo import api, fields, models
from odoo.exceptions import ValidationError

class RetailProduct(models.Model):
    _name = 'retail.product'
    _description = 'Retail Product'
    _order = 'name'
    image = fields.Binary(
        string='Image',
        attachment=True
        )
    name = fields.Char(
        string='Product Name',
        required=True,
    )
    sku = fields.Char(
        string='SKU',
        required=True,
    )
    _sku_unique = models.Constraint(
    'UNIQUE(sku)',
    'SKU must be unique.',
    )
    stock_ids = fields.One2many(
        'retail.stock',
        'product_id',
        string='Stock Records',
    )
    sale_ids = fields.One2many(
        'retail.sale',
        'product_id',
        string='Sales',
    )
    move_ids = fields.One2many('retail.stock.move','product_id',string='Stock Movements')

    available_quantity = fields.Integer(
        string='Available Quantity',
        compute='_compute_available_quantity',
        store=True,
    )

    @api.depends('move_ids.quantity')
    def _compute_available_quantity(self):
        for product in self:
            product.available_quantity = sum(product.move_ids.mapped('quantity'))

    sale_price = fields.Monetary(
        string='Selling Price',
        required=True,
    )
    cost_price = fields.Monetary(
        string='Cost Price',
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self.env.company.currency_id,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    @api.constrains('sale_price', 'cost_price')
    def _check_prices(self):
        for product in self:
            if product.sale_price < 0:
                raise ValidationError(
                    'Selling price cannot be negative.'
                )
            if product.cost_price < 0:
                raise ValidationError(
                    'Cost price cannot be negative.'
                )