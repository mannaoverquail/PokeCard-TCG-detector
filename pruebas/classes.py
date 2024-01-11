from marshmallow import Schema, fields, post_load
from pokemontcgsdk.card import Card


class AbilitySchema(Schema):
    name = fields.String()
    description = fields.String()


class WeaknessSchema(Schema):
    type = fields.String()
    value = fields.String()


class TCGPriceSchema(Schema):
    low = fields.Float()
    mid = fields.Float()
    high = fields.Float()
    market = fields.Float()
    directLow = fields.Float(allow_none=True)


class TCGPricesSchema(Schema):
    normal = fields.Nested(TCGPriceSchema, allow_none=True)
    holofoil = fields.Nested(TCGPriceSchema, allow_none=True)
    reverseHolofoil = fields.Nested(TCGPriceSchema, allow_none=True)
    firstEditionHolofoil = fields.Nested(TCGPriceSchema, allow_none=True)
    firstEditionNormal = fields.Nested(TCGPriceSchema, allow_none=True)


class TCGPlayerSchema(Schema):
    url = fields.String()
    updatedAt = fields.String()
    prices = fields.Nested(TCGPricesSchema)


class AttackSchema(Schema):
    name = fields.String()
    cost = fields.List(fields.String())
    convertedEnergyCost = fields.Integer()
    damage = fields.String()
    text = fields.String()


class CardImageSchema(Schema):
    small = fields.String()
    large = fields.String()


class CardmarketPricesSchema(Schema):
    averageSellPrice = fields.Float()
    lowPrice = fields.Float()
    trendPrice = fields.Float()
    # Agrega los otros campos aquí según tu estructura


class CardmarketSchema(Schema):
    url = fields.String()
    updatedAt = fields.String()
    prices = fields.Nested(CardmarketPricesSchema)


class LegalitySchema(Schema):
    unlimited = fields.String(allow_none=True)
    expanded = fields.String(allow_none=True)
    standard = fields.String(allow_none=True)


class ResistanceSchema(Schema):
    type = fields.String()
    value = fields.String()


class SetImageSchema(Schema):
    symbol = fields.String()
    logo = fields.String()


class SetSchema(Schema):
    id = fields.String()
    images = fields.Nested(SetImageSchema)
    legalities = fields.Nested(LegalitySchema)
    name = fields.String()
    printedTotal = fields.Integer()
    ptcgoCode = fields.String()
    releaseDate = fields.String()
    series = fields.String()
    total = fields.Integer()
    updatedAt = fields.String()


class CardSchema(Schema):
    abilities = fields.List(fields.Nested(AbilitySchema), allow_none=True)
    artist = fields.String()
    ancientTrait = fields.String(allow_none=True)
    attacks = fields.List(fields.Nested(AttackSchema))
    cardmarket = fields.Nested(CardmarketSchema)
    convertedRetreatCost = fields.Integer()
    evolvesFrom = fields.String()
    flavorText = fields.String()
    hp = fields.String()
    id = fields.String()
    images = fields.Nested(CardImageSchema)
    legalities = fields.Nested(LegalitySchema)
    regulationMark = fields.String(allow_none=True)
    name = fields.String()
    nationalPokedexNumbers = fields.List(fields.Integer())
    number = fields.String()
    rarity = fields.String()
    resistances = fields.List(fields.Nested(ResistanceSchema))
    retreatCost = fields.List(fields.String())
    rules = fields.String(allow_none=True)
    set = fields.Nested(SetSchema)
    subtypes = fields.List(fields.String())
    supertype = fields.String()
    tcgplayer = fields.Nested(TCGPlayerSchema)
    types = fields.List(fields.String())
    weaknesses = fields.Nested(WeaknessSchema, allow_none=True)

    @post_load
    def make_card(self, data, **kwargs):
        return Card(**data)
