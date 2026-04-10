from dateutil.relativedelta import relativedelta

from odoo import fields, models, api
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'

    #Campos del modelo
    price = fields.Float(string="Price")
    status = fields.Selection(string="Status", selection=[('accepted', 'Accepted'), ('refused', 'Refused')])
    validity = fields.Integer(default=7)

    #Campos calculados
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline', store=True)

    #Relaciones con otros modelos
    partner_id = fields.Many2one('res.partner', string="Partner", required=True)
    property_id = fields.Many2one('estate.property', string="Property", required=True, ondelete='cascade')
    property_type_id = fields.Many2one('estate.property.type', related='property_id.property_type_id', store=True)

    #Validaciones
    _check_price = models.Constraint('CHECK(price > 0)', 'El precio debe ser mayor a cero')

    #Campos Calculados
    @api.depends('validity')
    def _compute_date_deadline(self):
        for offer in self:
            base = offer.create_date or fields.Datetime.now()
            offer.date_deadline = base + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            base = (offer.create_date or fields.Datetime.now()).date()
            offer.validity = (offer.date_deadline - base).days

    #Acciones para los botones
    def action_accept(self):
        for offer in self:
            if offer.property_id.state == 'sold':
                raise UserError("Una propiedad vendida no puede aceptar ofertas")
            other_offers = offer.property_id.offer_ids - offer
            other_offers.write({'status': 'refused'})
            offer.status = 'accepted'
            offer.property_id._apply_accepted_offer(offer)
        return True

    def action_refuse(self):
        for offer in self:
            if offer.status == 'accepted':
                raise UserError("An accepted offer cannot be refused directly.")
            offer.status = 'refused'
        return True

    #Sobreescritura de funciones heredadas
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_rec = self.env['estate.property'].browse(vals.get('property_id'))
            self._check_offer_validity(property_rec, vals.get('price'))

        offers = super().create(vals_list)
        offers._update_property_state()
        return offers

    #Otras funciones
    def _check_offer_validity(self, property_rec, price):
        if property_rec.state in ('sold', 'cancelled'):
            raise UserError("No puede hacer ofertas a una propiedad vendida o cancelada")
        existing_prices = property_rec.offer_ids.mapped('price')
        if existing_prices and price <= max(existing_prices):
            raise UserError("Su oferta no puede ser menor a ofertas ya realizadas")

    def _update_property_state(self):
        for offer in self:
            if offer.property_id.state == 'new':
                offer.property_id.state = 'offer_received'