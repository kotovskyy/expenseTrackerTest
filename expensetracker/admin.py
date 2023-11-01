from django.contrib import admin

from .models import (Settings,
                     Account,
                     Transaction,
                     Currency,
                     Category) 
# Register your models here.
admin.site.register(Settings)
admin.site.register(Account)
admin.site.register(Transaction)
admin.site.register(Currency)
admin.site.register(Category)

