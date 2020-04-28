from tortoise.models import Model
from tortoise import fields

class LBUser(Model):
    balance = fields.IntField()
    canUseBot = fields.BooleanField()
    inventory = fields.JSONField()
    warnings = fields.JSONField()
    banUntil = fields.DatetimeField(null=True)

class LBGuild(Model):
    muteRole = fields.IntField()
    joinMesg = fields.CharField(max_length=1350, null=True)
