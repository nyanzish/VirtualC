from django import forms
from django.forms import ModelForm
from phonenumber_field.formfields import PhoneNumberField
from .models import Teacher_apply,Upload_topics,Subjects_overview,Comment,Message,Chat,UserProfile

# class Contentform(forms.ModelForm):
#     class Meta:
#         model = Content
#         fields = [
#         'topic',
#         'subject',
#         'class_level',
#         'content',
#         'notes',
#         'video'
#         ,]

#         widgets = {
#            #'topic': forms.TextInput(attrs={'class': 'form-control w-50'}),
#            'Notes': forms.FileInput(attrs={'class' : ''}),
#            'video': forms.ClearableFileInput(attrs={'class' : ' ','multiple': True}),


#         }

#     def __init__(self, *args, **kwargs):
#         super(Contentform, self).__init__(*args, **kwargs)
#         self.fields['topic'].widget.attrs.update({'class' : 'form-control w-50'})
#         self.fields['subject'].widget.attrs.update({'class' : 'form-control w-50'})
#         self.fields['class_level'].widget.attrs.update({'class' : 'form-control w-50'})
#         #self.fields['Notes'].widget.attrs.update({'class' : 'btn btn-primary w-25'})


class SignupForm(ModelForm):
    telephone = PhoneNumberField()
    telephone= forms.CharField(widget= forms.TextInput
                           (attrs={'placeholder':'+256702-0000'}))

    class Meta:
        model = UserProfile
        exclude = ['user','role','date_of_record','image']

        widgets = {
            'date_of_birth':forms.DateInput(attrs={'type':'date'}, format = 'YYYY-MM-DD'),

            }

        # date_of_birth = forms.DateField(widget = forms.DateInput(attrs={'placeholder':'YYYY-MM-DD','required':'required'})),

    def signup(self, request, user):
        user.userprofile.firstname = self.cleaned_data['firstname']
        user.userprofile.lastname = self.cleaned_data['lastname']
        user.userprofile.gender= self.cleaned_data['gender']
        user.userprofile.location = self.cleaned_data['location']
        user.userprofile.telephone = self.cleaned_data['telephone']
        user.userprofile.email = self.cleaned_data['email']
        user.userprofile.date_of_birth = self.cleaned_data['date_of_birth']
        user.userprofile.save()


class Uploadform(forms.ModelForm):
    class Meta:
        model = Upload_topics
        fields = [
        'subject',
        'class_level',
        'overview',
        'topic',
        'teacher',
        'content',
        'attached_file',
        'videos'
        ,]
        widgets = {
          'video': forms.ClearableFileInput(attrs={'class' : ' ','multiple': True}),


        }
# widgets = {
#         #'topic': forms.TextInput(attrs={'class': 'form-control w-50'}),
#         'Notes': forms.FileInput(attrs={'class' : ''}),
#         'video': forms.ClearableFileInput(attrs={'class' : ' ','multiple': True}),


#         }

class Overviewform(forms.ModelForm):
    class Meta:
        model = Subjects_overview
        fields = [
        'subject',
        'class_n',
        'teacher',
        'over_view',
        'duration',
        'image',
        'video',
        'price'
        ,]
        labels ={
                'video':'Video [leave blank if you donot a video at the moment, but you can still upload later!]',
        }

class Applyform(forms.ModelForm):
    class Meta:
        model = Teacher_apply
        fields = [
        'user',
        'schools_taught',
        'user_profile',
        'current_school',
        'level_of_teaching',
        'teacher_registration_id',
        'subject_one',
        'subject_two',
        'Brief_Self_description'
        ,]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        labels ={
                'body':' ',
        }

        widgets = {
            'body': forms.Textarea(attrs={'rows':4})}


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message']
        labels = {'message': ""}
        widgets = {
            'message': forms.Textarea(attrs={'rows':4})
            }


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['type','members','chat_title']
        labels = {
                'members':'Choose All People To Include In Chat (Include Yourself) ',
        }
        # widgets = {
        #      'members': forms.ModelMultipleChoiceField(attrs={'rows':4})
        #      }


