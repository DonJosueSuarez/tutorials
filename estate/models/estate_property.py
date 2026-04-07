from dateutil.relativedelta import relativedelta

from odoo import models, fields, api


class EstateProperty(models.Model):
    _name = "estate.property" #nombre de la tabla
    _description = "Property" #descripción del modelo

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Datetime("Date Availability", default=lambda self: fields.Datetime.now() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float()
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(string="Garden Orientation", selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')])
    active = fields.Boolean(default=False)
    state = fields.Selection(string="State", selection=[('new', 'New'),('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')], default='new')

    property_type_id = fields.Many2one(comodel_name='estate.property.type', string="Property Type")
    buyer_id = fields.Many2one(comodel_name='res.partner', string="Buyer")
    salesperson_id = fields.Many2one(comodel_name='res.users', string="Salesperson", default=lambda self: self.env.user)
    tag_ids = fields.Many2many(comodel_name='tag', string="Tags")
    offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_id', string="Offers")

    total_area = fields.Float(string="Total Area", compute='_compute_total_area')

    best_price = fields.Float(compute='_compute_best_price')

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