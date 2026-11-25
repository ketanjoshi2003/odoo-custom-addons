from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Stock(models.Model):
    _name = 'retail.stock'
    _description = 'Stock'
    name = fields.Char(
    string='Name',
    required=True,
    )
    quantity = fields.Integer(
    string='Quantity',
    required=True,
    )
    product_id = fields.Many2one(
    'retail.product',
    string='Product',
    required=True
    )
    date = fields.Datetime(
    string='Date',
    required=True,
    default=fields.Datetime.now,
    )
    price = fields.Monetary(
    string='Price',
    required=True
    )
    currency_id = fields.Many2one(
    'res.currency',
    string='Currency',
    required=True,
    readonly=True,
    default=lambda self: self.env.company.currency_id,
    )
    image = fields.Binary(
        string='Image',
        related='product_id.image',
        readonly=True,
    )
    @api.constrains('quantity', 'price')
    def _check_stock_values(self):
        for stock in self:
            if stock.quantity <= 0:
                raise ValidationError(
                    'Stock quantity must be greater than zero.'
                )
            if stock.price < 0:
                raise ValidationError(
                    'Stock price cannot be negative.'
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self.env['retail.stock.move'].create([
            {
                'product_id':rec.product_id.id,
                'quantity':rec.quantity,
                'move_type':'in',
                'stock_id':rec.id,
                'reference':rec.name,
                'date':rec.date,
            }
            for rec in records
        ])
        return records