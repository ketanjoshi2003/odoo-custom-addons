from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Profit(models.Model):
    _name = 'retail.profit'
    _description = 'Profit'

    sale_id = fields.Many2one(
    'retail.sale',
    string='Sale',
    required=True,
    ondelete='restrict',
    domain=[('state', '=', 'confirmed')],
    )

    date = fields.Date(string='Date', required=True)

    profit_amount = fields.Monetary(
    string='Profit Amount',
    compute='_compute_profit_amount',
    store=True,
    )

    currency_id = fields.Many2one(
    'res.currency',
    string='Currency',
    required=True,
    default=lambda self: self.env.company.currency_id,
    )

    @api.depends(
    'sale_id.total_amount',
    'sale_id.quantity',
    'sale_id.product_id.cost_price',
    )

    def _compute_profit_amount(self):
        for profit in self:
            if not profit.sale_id:
                profit.profit_amount = 0.0
                continue

            revenue = profit.sale_id.total_amount    
            cost = (
                profit.sale_id.quantity
                * profit.sale_id.product_id.cost_price
            )

            profit.profit_amount = revenue - cost
    
    @api.constrains('sale_id')
    def _check_sale_state(self):
        for profit in self:
            if profit.sale_id.state != 'confirmed':
                raise ValidationError(
                    'Profit can only be created for confirmed sales.'
                )