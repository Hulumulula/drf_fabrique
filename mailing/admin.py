from django.contrib import admin

from .models import *


class MessageAdmin(admin.ModelAdmin):
    model = Message
    # list_filter = '__all__'


class MessageInline(admin.TabularInline):
    model = Message


class ClientAdmin(admin.ModelAdmin):
    inlines = [MessageInline]
    # list_filter = '__all__'


class MailingAdmin(admin.ModelAdmin):
    inlines = [MessageInline]
    # list_filter = '__all__'


admin.site.register(Mailing, MailingAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Message, MessageAdmin)
