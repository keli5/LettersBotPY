from tortoise.models import Model
from tortoise import fields

class LBUser(Model):
    balance = fields.IntField()
    canUseBot = fields.BooleanField()
    inventory = fields.JSONField()

class LBGuild(Model):
    muteRole = fields.IntField()