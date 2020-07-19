from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.shortcuts import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from django.dispatch import receiver
from django.db.models.signals import post_save
from PIL import Image
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.db.models import *
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
genders = (
    ("M" , "Male"),
    ("F" , "Female")
)

level_of_teaching = (
    ("O-Level","Ordinary level"),
    ("A-Level","Advanced level"),
    ("Both" , "Both levels")
)


ACCOUNT = (
    ('Student', 'Student'),
    ('Teacher', 'Teacher'),
    ('User', 'User'),
)

CATEGORY_CLASS = (
    ('S1', 'S1'),
    ('S2', 'S2'),
    ('S3', 'S3'),
    ('S4', 'S4'),
    ('S5', 'S5'),
    ('S6', 'S6'),

)

CATEGORY_SUBJECTS = (
    ('Mathematics', 'Mathematics'),
    ('Physics', 'Physics'),
    ('Chemistry', 'Chemistry'),
    ('Biology', 'Biology'),
    ('History', 'History'),
    ('Geography', 'Geography'),
    ('English', 'English'),
    ('Islam','Islam'),
    ('Cre', 'Cre'),
    ('Agriculture', 'Agriculture'),
    ('Computer', 'Computer'),
    ('Economics', 'Economics'),
    ('Divinity', 'Divinity'),
    ('Literature', 'Literature'),
    ('TechnicalDrawing', 'TechnicalDrawing'),
    ('Art', 'Art'),
    ('French', 'French'),
    ('German', 'German'),
    ('Lugbara_Ti', 'Lugbara_Ti'),
    ('Chinese', 'Chinese'),
    ('Luganda', 'Luganda'),
    ('GeneralPaper','GeneralPaper'),

)

class UserProfile(models.Model):
    #dateofbirth
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=30)
    lastname = models.CharField(max_length=30)
    gender = models.CharField(max_length=20,choices=genders)
    location = models.CharField(max_length=30)
    telephone = PhoneNumberField(null=False, blank=False)
    email = models.EmailField()
    #username = models.CharField(max_length=30)
    #password = models.CharField(max_length=30)
    image = models.ImageField(default='default.png')
    date_of_birth = models.DateTimeField(null=True)
    role = models.CharField( max_length=8,choices=ACCOUNT,default='User')
    date_of_record = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

    # def save(self):
    #     super().save()
    #     img = Image.open(self.image.path)
    #     if img.height > 300 or img.width > 300 :
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.image.path)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


class Class_table(models.Model):
    name = models.CharField( max_length=30)
    date_of_record = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Subjects(models.Model):
    subject_name = models.CharField(max_length=30)
    subject_image = models.ImageField()
    date_of_record = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.subject_name

    def get_absolute_url(self):
        return reverse("e_learning:push", args=[str(self.pk)
        ])

    def get_start_discussion_url(self):
        return reverse("e_learning:start_discussion", args=[str(self.pk)
        ])

class Recommend_Subjects_Table(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=30)
    class_level = models.CharField(max_length=30)
    book_title = models.CharField(max_length=30)
    book_cover_image = models.ImageField(default='book_vector.png')
    attach_book = models.FileField()
    recommended_by = models.CharField(max_length=30)
    date_of_record = models.DateTimeField(default=timezone.now)

    def get_the_book(self):
        return reverse("e_learning:delete_book", args=[str(self.pk)
        ])

class Teacher_apply(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    schools_taught = models.CharField( max_length=30)
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    current_school = models.CharField(  max_length=30)
    level_of_teaching = models.CharField( max_length=30 , choices=level_of_teaching )
    teacher_registration_id = models.CharField(  max_length=100)
    subject_one = models.CharField(max_length=20,choices=CATEGORY_SUBJECTS)
    subject_two = models.CharField(max_length=20,choices=CATEGORY_SUBJECTS)
    Brief_Self_description = models.TextField()
    date_of_record = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "%s - %s" % (self.user, self.current_school)
        #return self.current_school
    def get_absolute_urls(self):
        return reverse("e_learning:accept", args=[str(self.pk)
        ])

class Subjects_overview(models.Model):
    #duration
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    teacher =models.ForeignKey(Teacher_apply ,on_delete=models.CASCADE)
    over_view = models.TextField()
    image = models.ImageField()
    video = models.FileField(null=True, blank=True,default='comingsoon_overview.mp4')
    duration = models.DurationField(help_text=('[DD] [HH:[MM:]]ss[.uuuuuu] format---- eg 30 00:00 to mean 30days'))
    date_of_record = models.DateTimeField(default=timezone.now)
    price = models.IntegerField(help_text=('UGX'))

    def __str__(self):
        return "%s -- %s" % (self.teacher, self.subject)
        #return self.current_school

    def get_absolute_url(self):
        return reverse("e_learning:subject_overview", args=[str(self.pk)
        ])

    def get_teacher_to_alert(self):
        return reverse("e_learning:teacher_comment_topics", args=[str(self.pk)
        ])

    def get_subject_uploaded_url(self):
        return reverse("e_learning:my_uploaded", args=[str(self.pk)
        ])

    def edit_subject_uploaded_url(self):
        return reverse("e_learning:edit_my_uploaded", args=[str(self.pk)
        ])

class Subscription(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    subject_overview = models.ForeignKey(Subjects_overview ,on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher_apply ,on_delete=models.CASCADE)
    Amount = models.IntegerField()
    active = models.BooleanField(default=False)
    date_of_subscription = models.DateTimeField(default=timezone.now)
    duration = models.DurationField()

    def get_subject_start_learning_id(self):
        return reverse("e_learning:start_reading", args=[str(self.pk)
        ])

class Assignments_Table(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject_overview = models.ForeignKey(Subjects_overview,on_delete=models.CASCADE)
    assignment_title = models.CharField(max_length=300)
    attach_assignment = models.FileField()
    date_of_record = models.DateTimeField(default=timezone.now)

    def add_submissions(self):
        return reverse("e_learning:add_submission", args=[str(self.pk)
        ])

class Response_Table(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignments = models.ForeignKey(Assignments_Table,on_delete=models.CASCADE)
    add_response = models.FileField()
    date_of_record = models.DateTimeField(default=timezone.now)

class PaymentRecords(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    user_profile = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    subject_overview = models.ForeignKey(Subjects_overview ,on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher_apply ,on_delete=models.CASCADE)
    Amount = models.IntegerField()
    active = models.BooleanField(default=False)
    date_of_subscription = models.DateTimeField(default=timezone.now)
    duration = models.DurationField()


class Upload_topics(models.Model):
    overview = models.ForeignKey(Subjects_overview ,on_delete=models.CASCADE)
    class_level = models.CharField( max_length=60)
    subject = models.CharField( max_length=60)
    teacher = models.ForeignKey(Teacher_apply ,on_delete=models.CASCADE)
    topic = models.CharField( max_length=900)
    content = RichTextUploadingField()
    videos = models.FileField(null=True, blank=True,default='comingsoon_topic.mp4')
    attached_file = models.FileField()
    date_of_record = models.DateTimeField(default=timezone.now)

    def get_video_url(self):
        return reverse("e_learning:video", args=[str(self.pk)
        ])

    def get_document_url(self):
        return reverse("e_learning:document", args=[str(self.pk)
        ])

    def get_open_content(self):
        return reverse("e_learning:open_content", args=[str(self.pk)
        ])

    def get_teacher_alerts(self):
        return reverse("e_learning:teacher_alerts", args=[str(self.pk)
        ])

    def get_edit_url(self):
        return reverse("e_learning:edit_my_topic", args=[str(self.pk)
        ])

    def get_delete_url(self):
        return reverse("e_learning:topic_delete", args=[str(self.pk)
        ])
    
    def get_student_video_url(self):
        return reverse("e_learning:student_video", args=[str(self.pk)
        ])

class Comment(models.Model):
    user_image = models.CharField(default='default.png',max_length=800)
    topic = models.ForeignKey(Upload_topics,on_delete=models.CASCADE,related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True, blank=True,on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)

    def children(self):
        return Comment.objects.get(parent=self)
    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True


class ChatManager(models.Manager):
    use_for_related_fields = True
    def unreaded(self, user=None):
        qs = self.get_queryset().exclude(last_message__isnull=True).filter(last_message__is_readed=False)
        return qs.exclude(last_message__author=user) if user else qs


class Chat(models.Model):
    DIALOG = 'D'
    CHAT = 'C'
    CHAT_TYPE_CHOICES = (
        (CHAT, _('Chat')),
    )

    type = models.CharField(
        _('?YPE'),
        max_length=1,
        choices=CHAT_TYPE_CHOICES,
        default=CHAT
    )
    members = models.ManyToManyField(Teacher_apply, verbose_name=_("Member"))
    last_message = models.ForeignKey('Message', related_name='last_message', null=True, blank=True, on_delete=models.SET_NULL)
    chat_title = models.CharField(max_length = 50, default='hello')

    objects = ChatManager()

    #@models.permalink
    def get_absolute_url(self):
        return reverse("e_learning:messages", args=[str(self.pk)])
    # def get_absolute_url(self):
    #     return 'users:messages', (), {'chat_id': self.pk }

class ChatRoom(models.Model):
    title= models.CharField(max_length=800)
    user_profile = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_record = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title

    def get_chat_url(self):
        return reverse("e_learning:conversation", args=[str(self.pk)])

class ChatComment(models.Model):
    user_image = models.CharField(default='default.png',max_length=800)
    topic = models.ForeignKey(ChatRoom,on_delete=models.CASCADE,related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True, blank=True,on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return 'ChatComment {} by {}'.format(self.body, self.name)

    def children(self):
        return ChatComment.objects.get(parent=self)
    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True
        

class StudentChatComment(models.Model):
    user_image = models.CharField(default='default.png',max_length=800)
    topic = models.ForeignKey(Subjects,on_delete=models.CASCADE,related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True, blank=True,on_delete=models.CASCADE, related_name='replies')

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return 'StudentChatComment {} by {}'.format(self.body, self.name)

    def children(self):
        return StudentChatComment.objects.get(parent=self)
    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True


class Message(models.Model):
    chat = models.ForeignKey(Chat, verbose_name=_("Chat"),on_delete=models.CASCADE)
    author = models.ForeignKey(User, verbose_name=_("User") ,on_delete=models.CASCADE)
    message = models.TextField(_("Message"))
    pub_date = models.DateTimeField(_('Message date'), default=timezone.now)
    is_readed = models.BooleanField(_('Readed'), default=False)


    class Meta:
        ordering=['pub_date']

    def __str__(self):
        return self.message


class Mathematics(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Physics(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Chemistry(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Biology(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Geography(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class English(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class History(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Islam(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class CRE(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Agriculture(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Computer(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class TechnicalDrawing(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Art(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class French(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class German(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Chinese(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Luganda(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class GeneralPaper(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Economics(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Divinity(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Literature(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

class Lugbara_Ti(models.Model):
    subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)
    class_n = models.ForeignKey(Class_table,on_delete=models.CASCADE)
    topic_name = models.CharField( max_length=300)
    date_of_record = models.DateTimeField(default=timezone.now)

