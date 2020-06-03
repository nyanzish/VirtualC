from django.contrib import admin
from .models import(
    UserProfile,
    Class_table,
    Subjects,
    Teacher_apply,
    Subjects_overview,
    Subscription,
    PaymentRecords,
    Upload_topics,
    Mathematics,
    Physics,
    Chemistry,
    Biology,
    Geography,
    English,
    History,
    Islam,
    CRE,
    Agriculture,
    Computer,
    TechnicalDrawing,
    Art,
    French,
    German,
    Chinese,
    Luganda,
    GeneralPaper,
    Comment,
    Chat,
    Message,
    Recommend_Subjects_Table,
    ChatRoom,
    ChatComment
)


class ChatAdmin(admin.ModelAdmin):
    #autocomplete_fields = ['members']
    search_fields = ('members',)
    actions = ['fix_last_messages']

    def fix_last_messages(self, request, queryset):
        for chat in queryset.all():
            chat.last_message = chat.message_set.all().order_by('-pub_date').first()
            chat.save(update_fields=['last_message'])

    fix_last_messages.short_description = "Fix last messages"


class MessageAdmin(admin.ModelAdmin):
    autocomplete_fields = ['chat', 'author']
    list_display = ('chat', 'author', 'message', 'pub_date', 'is_readed')


# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Class_table)
admin.site.register(Subjects)
admin.site.register(Teacher_apply)
admin.site.register(Subjects_overview)
admin.site.register(Upload_topics)
admin.site.register(Subscription)
admin.site.register(PaymentRecords)
admin.site.register(Mathematics)
admin.site.register(Physics)
admin.site.register(Chemistry)
admin.site.register(Biology)
admin.site.register(Geography)
admin.site.register(English)
admin.site.register(History)
admin.site.register(Islam)
admin.site.register(CRE)
admin.site.register(Agriculture)
admin.site.register(Computer)
admin.site.register(TechnicalDrawing)
admin.site.register(Art)
admin.site.register(French)
admin.site.register(German)
admin.site.register(Chinese)
admin.site.register(Luganda)
admin.site.register(Recommend_Subjects_Table)
admin.site.register(GeneralPaper)
admin.site.register(Chat,ChatAdmin)
admin.site.register(Message,MessageAdmin)
admin.site.register(ChatRoom)
admin.site.register(ChatComment)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'topic', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)