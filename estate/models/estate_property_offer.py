from dateutil.relativedelta import relativedelta

from odoo import fields, models, api

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'

    price = fields.Float(string="Price")
    status = fields.Selection(string="Status", selection=[('accepted', 'Accepted'), ('refused', 'Refused')])
    partner_id = fields.Many2one('res.partner', string="Partner", required=True)
    property_id = fields.Many2one('estate.property', string="Property", required=True)

    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline', store=True)

    @api.depends('validity')
    def _compute_date_deadline(self):
        for offer in self:
            base = offer.create_date or fields.Datetime.now()
            offer.date_deadline = base + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            base = (offer.create_date or fields.Datetime.now()).date()
            offer.validity = (offer.date_deadline - base).days