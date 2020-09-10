from tortoise.models import Model
from tortoise import fields


class LBUser(Model):
    balance = fields.FloatField()
    canUseBot = fields.BooleanField()
    inventory = fields.JSONField()


class LBGuild(Model):
    muteRole = fields.IntField(null=True)
    disabledCommands = fields.JSONField()
    blacklisted = fields.BooleanField()
    joinMesg = fields.CharField(max_length=1350, null=True)
    joinMesgChannel = fields.IntField(null=True)
