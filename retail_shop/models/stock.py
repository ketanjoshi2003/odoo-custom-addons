from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Stock(models.Model):
    _name = 'retail.stock'
    _description = 'Stock'

    name = fields.Char(string='Name', required=True)
    quantity = fields.Integer(string='Quantity', required=True)
    product_id = fields.Many2one('retail.product', string='Product', required=True)
    date = fields.Date(string='Date', required=True)
    price = fields.Monetary(string='Price', required=True)
    currency_id = fields.Many2one(
    'res.currency',
    string='Currency',
    required=True,
    default=lambda self: self.env.company.currency_id,
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