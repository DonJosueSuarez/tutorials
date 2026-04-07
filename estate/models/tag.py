from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = 'tag'
    _description = 'Estate Property Tag'

    name = fields.Char(required=True)

    _check_unique_tag = models.Constraint('UNIQUE(name)', 'El nombre de la etiqueta debe ser único')