# Generated by Django 3.0.5 on 2020-05-04 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_learning', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='chat_title',
            field=models.CharField(default='hello', max_length=50),
        ),
        migrations.AlterField(
            model_name='teacher_apply',
            name='subject_one',
            field=models.CharField(choices=[('Mathematics', 'Mathematics'), ('Physics', 'Physics'), ('Chemistry', 'Chemistry'), ('Biology', 'Biology'), ('History', 'History'), ('Geography', 'Geography'), ('English', 'English'), ('Islam', 'Islam'), ('CRE', 'CRE'), ('Agriculture', 'Agriculture'), ('Computer', 'Computer'), ('TechnicalDrawing', 'TechnicalDrawing'), ('Art', 'Art'), ('French', 'French'), ('German', 'German'), ('Chinese', 'Chinese'), ('Luganda', 'Luganda'), ('GeneralPaper', 'GeneralPaper')], max_length=20),
        ),
        migrations.AlterField(
            model_name='teacher_apply',
            name='subject_two',
            field=models.CharField(choices=[('Mathematics', 'Mathematics'), ('Physics', 'Physics'), ('Chemistry', 'Chemistry'), ('Biology', 'Biology'), ('History', 'History'), ('Geography', 'Geography'), ('English', 'English'), ('Islam', 'Islam'), ('CRE', 'CRE'), ('Agriculture', 'Agriculture'), ('Computer', 'Computer'), ('TechnicalDrawing', 'TechnicalDrawing'), ('Art', 'Art'), ('French', 'French'), ('German', 'German'), ('Chinese', 'Chinese'), ('Luganda', 'Luganda'), ('GeneralPaper', 'GeneralPaper')], max_length=20),
        ),
    ]
