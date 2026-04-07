from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property" #nombre de la tabla
    _description = "Property" #descripción del modelo

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Datetime("Date Availability", default=lambda self: fields.Datetime.now() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(string="Garden Orientation", selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    active = fields.Boolean(default=False)
    state = fields.Selection(string="State", readonly=True, selection=[('new', 'New'),('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')], default='new')

    property_type_id = fields.Many2one(comodel_name='estate.property.type', string="Property Type")
    buyer_id = fields.Many2one(comodel_name='res.partner', string="Buyer")
    salesperson_id = fields.Many2one(comodel_name='res.users', string="Salesperson", default=lambda self: self.env.user)
    tag_ids = fields.Many2many(comodel_name='tag', string="Tags")
    offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_id', string="Offers")

    total_area = fields.Float(string="Total Area", compute='_compute_total_area')

    best_price = fields.Float(compute='_compute_best_price')

    _check_expected_price = models.Constraint('CHECK(expected_price > 0)', 'El Expected Price debe ser un valor mayor a cero')
    _check_selling_price = models.Constraint('CHECK(selling_price > 0)', 'El valor de venta debe ser mayor a cero')

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price_percentage(self):
        for property in self:
            if float_is_zero(property.selling_price, precision_rounding=0.01):
                continue
            minimum_price = property.expected_price * 0.9
            if float_compare(property.selling_price, minimum_price, precision_rounding=0.01) < 0:
                raise ValidationError("El valor de venta debe ser mayor o igual al 90% del valor esperado")

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for property in self:
            property.total_area = property.living_area + property.garden_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for property in self:
            prices = property.offer_ids.mapped('price')
            property.best_price = max(prices) if prices else 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Una propiedad vendida no puede ser cancelada")
            record.state = 'cancelled'
            return True

    def action_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("Una propiedad cancelada no puede ser vendida")
            record.state = 'sold'
            return True

    def _apply_accepted_offer(self, offer):
        self.ensure_one()
        self.buyer_id = offer.partner_id
        self.selling_price = offer.price
        self.state = 'offer_accepted'