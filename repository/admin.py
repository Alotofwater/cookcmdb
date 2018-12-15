from django.contrib import admin
from repository import models
# Register your models here.
admin.site.register(models.AdminInfo)
admin.site.register(models.UserProfile)
admin.site.register(models.UserGroup)
admin.site.register(models.BusinessUnit)
admin.site.register(models.IDC)
admin.site.register(models.Server)
admin.site.register(models.Disk)
admin.site.register(models.NIC)
admin.site.register(models.Memory)
admin.site.register(models.Tag)

