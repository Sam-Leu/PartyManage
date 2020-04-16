from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Admin)
admin.site.register(models.Member)
admin.site.register(models.Activist)
admin.site.register(models.RewardAndPunish)
admin.site.register(models.RewardPunishInfo)
admin.site.register(models.MeetingRecord)