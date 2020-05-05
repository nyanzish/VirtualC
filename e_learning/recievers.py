from django.db.models.signals import post_save
from django.dispatch import receiver
 
from .models import Message
 
 
# message object save handler
@receiver(post_save, sender=Message)
def post_save_comment(sender, instance, created, **kwargs):
    # if the object was created
    if created:
        # we indicate to the chat room where this message is located, that this is the last message
        instance.chat.last_message = instance
        # and update this foreign chat key
        instance.chat.save(update_fields=['last_message'])