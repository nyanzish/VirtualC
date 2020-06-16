from django.shortcuts import render, get_object_or_404
from .forms import Overviewform,Uploadform,Applyform,MessageForm,ChatForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.http import FileResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from .forms import CommentForm,ChatCommentForm,ChatRoomForm,StudentChatCommentForm
import re
import datetime
from django.db.models import Q
from django.core.mail import send_mail,BadHeaderError,EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import get_template
from django.http import HttpResponse
from .models import (
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
    ChatComment,
    StudentChatComment

)

# Create your views here.
def index(request):
    global lista_two
    lista_one = []
    lista_two = []
    lista_three = []
    lista_four = []
    lista_all = []
    subjects = Subjects.objects.all()
    for value in subjects:
        lista_one.append(value.subject_image.url)
        lista_two.append(value.subject_name)
        lista_four.append(value.id)
        subject_o = Subjects_overview.objects.filter(subject = value.id).count()
        lista_three.append(subject_o)
    # #print(lista_one)
    # print(lista_two)
    # print(lista_three)
    for x in range(len(lista_one)):
        all_variables = lista_one[x],lista_two[x],lista_three[x],lista_four[x]
        lista_all.append(all_variables)
    print(lista_all)
    page = request.GET.get('page', 1)
    paginator = Paginator(lista_all,8)
    # lista_all= paginator.page(page)
    try:
        lista_all = paginator.page(page)
    except PageNotAnInteger:
        lista_all = paginator.page(1)
    except EmptyPage:
        lista_all = paginator.page(paginator.num_pages)

    context = {
        "lista_all": lista_all
        }
    return render(request,'index.html',context)

@login_required
def Search(request):
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET.get('q')
        print(query_string)
        overview = Subjects_overview.objects.filter(subject__subject_name__icontains = query_string)|Subjects_overview.objects.filter(class_n__name__icontains = query_string)
        context = {
            'overview':overview,
            'query_string':query_string
        }
        return render(request,'student_homepage.html',context)
    else:
        overview = None
        query_string = request.GET.get('q')
        context = {
                'overview':overview,
                'query_string':query_string
        }
        return render(request,'student_homepage.html',context)

def subject_get(request):
    sub_id = request.POST.get('get_subject')
    # ids=[]
    # for name in lista_two:
    #     sub_id = request.POST.get(f'{name}')
    #     ids.append(sub_id)
    #     print(sub_id,'iiiiiiiiiiiiiiiiiiiiiiiiiii')

    # print(ids)
    subject_details = Subjects_overview.objects.filter(subject = sub_id)
    subject_detailz = Subjects_overview.objects.filter(subject = sub_id).count()
    print(subject_detailz)
    # print(subject_details)
    #counter = sub_id
    #for x
    for sub_details in subject_details:
        print(sub_details)

    context = {
        'subject_details' : subject_details,
    }

    return render(request,'particular_.html',context)
IMAGE_FILE_TYPES2 = ['png', 'jpg', 'jpeg']
@login_required
def my_profile(request):
    content = UserProfile.objects.get(user= request.user)
    print(content)
    context = {
        'content':content,
        }

    if request.method == "POST":
        content.firstname = request.POST.get('first_name')
        content.lastname = request.POST.get('last_name')
        content.location = request.POST.get('location')
        content.telephone = request.POST.get('contact')
        #if 'image' in request.FILES:
        if request.FILES:
            content.image = request.FILES.get('myfile')
            file_type = content.image.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES2:
                messages.warning(request, 'Please check the image you uploaded')
                return render(request, 'error.html')
            else:
                content.save()
        content.save()
        messages.success(request, 'Profile details updated.')
    return render(request,'my_profile.html',context)

@login_required
def settings_page(request):
    content = UserProfile.objects.get(user= request.user)
    print(content)
    context = {
        'content':content,
        }
    return render(request,'settings_page.html',context)

@login_required
def delete_my_account(request):
    user = request.user
    user.is_active = False
    user.save()
    #messages.success(request,'Your account was deleted.')
    return redirect('e_learning:index')

@login_required
def upload(request):

    #new_record=
    teacher_id=Teacher_apply.objects.get(user=request.user.id)
    print(teacher_id.id)
    subject=Teacher_apply.objects.filter(user=request.user.id)
    global class_id
    global subject_id
    class_id=request.POST.get('class_id')
    subject_id=request.POST.get('subject_id')
    print(class_id,subject_id,'2222222222222222')
    try:
        overview=Subjects_overview.objects.get(class_n__exact=class_id,subject__exact=subject_id,teacher=teacher_id.id)
        print(overview)

    except ObjectDoesNotExist:
        messages.info(request, "You do not have an overview for this particular class ,First create an overview.")
        return redirect('e_learning:overview')
    return redirect('e_learning:upload_to')

def name ():
    sub_results=Subjects.objects.get(id=subject_id)
    return sub_results.subject_name

DOC_FILE_TYPES = ['pdf']
VID_FILE_TYPES = ['mp4']
@login_required
def upload_to(request):

    teacher_id=Teacher_apply.objects.get(user=request.user.id)
    current_teacher = teacher_id.id
    #print(teacher_id.id)
    #print(class_id,subject_id,'88888888888888888')
    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0
        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()
        try:
            overview=Subjects_overview.objects.get(class_n__exact=class_id,subject__exact=subject_id,teacher=teacher_id)
            print(overview)

            subject=Teacher_apply.objects.filter(user=request.user.id)
            subject_one=subject[0].subject_one
            subject_two=subject[0].subject_two
            #print(class_id,subject_id)
            # sub_results=Subjects.objects.get(id=subject_id)
            # subject_table=sub_results.subject_name
            topics=eval(name()).objects.filter(class_n__exact=class_id,subject__exact=subject_id)
            result= topics
            #print(topics)
            form = Uploadform(initial={'overview': overview.id,'teacher':teacher_id.id,'class_level':str(class_id),'subject':str(subject_id)})
            context= {
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_chats':no_of_chats,
                'form':form,
                'result':result


            }
            
            if request.method=='POST':
                form = Uploadform(request.POST, request.FILES)

                form.fields['overview'].initial=overview.id
                form.fields['overview'].type='hidden'
                form.fields['teacher'].initial=teacher_id
                form.fields['teacher'].value=teacher_id
                form.fields['teacher'].type='hidden'
                form.fields['class_level'].initial=class_id
                form.fields['class_level'].value=class_id
                form.fields['class_level'].type='hidden'
                form.fields['subject'].initial=subject_id
                form.fields['class_level'].value=subject
                form.fields['subject'].type='hidden'

                topic = request.POST.get('topic')
                print(topic)
                save_form = form.save(commit=False)
                #overview_value = form.cleaned_data.get('overview')
                form.cleaned_data.get('overview')
                form.cleaned_data.get('teacher')
                form.cleaned_data.get('class_level')
                form.cleaned_data.get('subject')
                form.cleaned_data.get('topic')
                form.cleaned_data.get('content')

                teacher = request.POST.get('teacher')
                print(teacher)
                content =request.POST.get('content')
                print(content)
                class_level =request.POST.get('class_level')
                print(class_level)
                subject = request.POST.get('subject')
                print(subject)
                save_form.attached_file = request.FILES['attached_file']
                file_type = save_form.attached_file.url.split('.')[-1]
                file_type = file_type.lower()
                if file_type not in DOC_FILE_TYPES:
                    messages.warning(request, 'Please check the document you uploaded')
                    return render(request, 'error.html')
                save_form.video= request.FILES['videos']

                file_type2 = save_form.video.url.split('.')[-1]
                file_type2 = file_type2.lower()
                if file_type2 not in VID_FILE_TYPES:
                    messages.warning(request, 'Please check the video you uploaded')
                    return render(request, 'error.html')
                attached_file = request.FILES['attached_file']
                print(attached_file)
                videos = request.FILES['videos']
                print(videos)
                save_form.save()
                # upload_topics=Upload_topics(
                #     overview=overview,
                #     teacher=teacher_id,
                #     class_level=class_level,
                #     subject=subject,
                #     topic=topic,
                #     content=content,
                #     attached_file=attached_file,
                #     videos= videos

                # )
                # upload_topics.save()
                print('done_saving')
                messages.info(request, "Topic successfully added")


            return render(request,'upload.html',context)
        except NameError:
            return redirect('e_learning:teacher_homepage')
    else:
        try:
            overview=Subjects_overview.objects.get(class_n__exact=class_id,subject__exact=subject_id,teacher=teacher_id)
            print(overview)

            subject=Teacher_apply.objects.filter(user=request.user.id)
            subject_one=subject[0].subject_one
            subject_two=subject[0].subject_two
            #print(class_id,subject_id)
            # sub_results=Subjects.objects.get(id=subject_id)
            # subject_table=sub_results.subject_name
            topics=eval(name()).objects.filter(class_n__exact=class_id,subject__exact=subject_id)
            result= topics
            #print(topics)
            form = Uploadform(initial={'overview': overview.id,'teacher':teacher_id.id,'class_level':str(class_id),'subject':str(subject_id)})
            # context= {
            #     'subject_two':subject_two,
            #     'subject_one':subject_one,
            #     'form':form,
            #     'result':result


            # }
            counter_list=[]
            for my_studnts in list_of_students:
                print(my_studnts)
                
                teacher_students=Subscription.objects.filter(teacher=current_teacher)
                for my_studnt in teacher_students:
                    print(my_studnt,my_studnt.student.id)

                retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
                counter = retrieve_my_comments.count()
                counter_list.append(counter)
                print(counter,'999000000000')

                no_of_chats = ChatRoom.objects.all()
                no_of_chats = no_of_chats.count()

                retrieved_commented = retrieve_my_comments[:4]
                print(retrieved_commented)

                for notification in retrieved_commented:
                    notifications = notification.body
            counter_list_no = sum(counter_list)
            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter_list_no,
                'no_of_students':no_of_students,
                'no_of_chats':no_of_chats,
                'retrieved_commented':retrieved_commented,
                'form':form,
                'result':result
            }
            if request.method=='POST':
                form = Uploadform(request.POST, request.FILES)

                form.fields['overview'].initial=overview.id
                form.fields['overview'].type='hidden'
                form.fields['teacher'].initial=teacher_id
                form.fields['teacher'].value=teacher_id
                form.fields['teacher'].type='hidden'
                form.fields['class_level'].initial=class_id
                form.fields['class_level'].value=class_id
                form.fields['class_level'].type='hidden'
                form.fields['subject'].initial=subject_id
                form.fields['class_level'].value=subject
                form.fields['subject'].type='hidden'

                topic = request.POST.get('topic')
                print(topic)
                save_form = form.save(commit=False)
                #overview_value = form.cleaned_data.get('overview')
                form.cleaned_data.get('overview')
                form.cleaned_data.get('teacher')
                form.cleaned_data.get('class_level')
                form.cleaned_data.get('subject')
                form.cleaned_data.get('topic')
                form.cleaned_data.get('content')

                teacher = request.POST.get('teacher')
                print(teacher)
                content =request.POST.get('content')
                print(content)
                class_level =request.POST.get('class_level')
                print(class_level)
                subject = request.POST.get('subject')
                print(subject)
                save_form.attached_file = request.FILES['attached_file']
                file_type = save_form.attached_file.url.split('.')[-1]
                file_type = file_type.lower()
                if file_type not in DOC_FILE_TYPES:
                    messages.warning(request, 'Please check the document you uploaded')
                    return render(request, 'error.html')
                save_form.video= request.FILES['videos']

                # file_type2 = save_form.video.split('.')[-1]
                # file_type2 = file_type2.lower()
                # if file_type2 not in VID_FILE_TYPES:
                #     messages.warning(request, 'Please check the video you uploaded')
                #     return render(request, 'error.html')
                attached_file = request.FILES['attached_file']
                print(attached_file)
                videos = request.FILES['videos']
                print(videos)
                save_form.save()
                # upload_topics=Upload_topics(
                #     overview=overview,
                #     teacher=teacher_id,
                #     class_level=class_level,
                #     subject=subject,
                #     topic=topic,
                #     content=content,
                #     attached_file=attached_file,
                #     videos= videos

                # )
                # upload_topics.save()
                print('done_saving')
                messages.info(request, "Topic successfully added")


            return render(request,'upload.html',context)
        except NameError:
            return redirect('e_learning:teacher_homepage')

VID_FILE_TYPES = ['mp4']
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']
@login_required
def overview(request):
    form = Overviewform()
    teacher_id=Teacher_apply.objects.get(user=request.user.id)
    print(teacher_id.id)
    try:
        print(class_id,subject_id,'999999999999999999')
        class_object= get_object_or_404(Class_table, id=int(class_id))
        subject_object= get_object_or_404(Subjects, id=int(subject_id))
        form = Overviewform(initial={'subject': subject_object.id,'teacher':teacher_id.id,'class_n':class_object.id})

        subject=Teacher_apply.objects.filter(user=request.user.id)
        subject_one=subject[0].subject_one
        subject_two=subject[0].subject_two

        current_teacher = teacher_id.id
        print(current_teacher,'kkkkkkkk')

        list_of_students = []

        retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
        no_of_students = retrieve_my_students.count()
        for students_retrieved in retrieve_my_students:
            my_student = students_retrieved.student
            list_of_students.append(my_student)
        print(list_of_students,'99999999999999999999')

        if len(list_of_students) == 0:
            counter = 0
            no_of_students = 0
            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()

            context={
                     'subject_two':subject_two,
                    'subject_one':subject_one,
                    'counter':counter,
                    'no_of_chats':no_of_chats,
                    'no_of_students':no_of_students,
                    'form':form

                }
            if request.method=='POST':
                form = Overviewform(request.POST, request.FILES)

                form.fields['subject'].initial=subject_object.id
                form.fields['class_n'].initial=class_object.id
                form.fields['teacher'].initial=teacher_id
                form.fields['subject'].value=subject_object.id
                form.fields['class_n'].value=class_object.id
                form.fields['teacher'].value=teacher_id.id
                #overview_value = form.cleaned_data.get('overview')
                save_form = form.save(commit=False)
                form.cleaned_data.get('over_view')
                form.cleaned_data.get('teacher')
                form.cleaned_data.get('class_n')
                form.cleaned_data.get('subject')
                form.cleaned_data.get('duration')
                form.cleaned_data.get('price')
                save_form.image= request.FILES['image']
                file_type = save_form.image.url.split('.')[-1]
                file_type = file_type.lower()
                if file_type not in IMAGE_FILE_TYPES:
                    messages.warning(request, 'Please check the image you uploaded')
                    return render(request, 'error.html')
                # else:
                #     print('image in')
                try:
                    save_form.video= request.FILES['video']
                    file_type2 = save_form.video.url.split('.')[-1]
                    file_type2 = file_type2.lower()
                    if file_type2 not in VID_FILE_TYPES:
                        messages.warning(request, 'Please check the video you uploaded')
                        return render(request, 'error.html')
                except:
                    pass
                save_form.save()
                print('done_saving')
                messages.info(request, "Overview successfully added,now continue to the class")
                return redirect('e_learning:teacher_homepage')
            return render(request,'overview.html',context)
        else:
            counter_list=[]
            for my_studnts in list_of_students:
                print(my_studnts)
                
                teacher_students=Subscription.objects.filter(teacher=current_teacher)
                for my_studnt in teacher_students:
                    print(my_studnt,my_studnt.student.id)

                retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
                counter = retrieve_my_comments.count()
                counter_list.append(counter)
                print(counter,'999000000000')

                no_of_chats = ChatRoom.objects.all()
                no_of_chats = no_of_chats.count()

                retrieved_commented = retrieve_my_comments[:4]
                print(retrieved_commented)

                for notification in retrieved_commented:
                    notifications = notification.body
            counter_list_no = sum(counter_list)
            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter_list_no,
                'no_of_students':no_of_students,
                'no_of_chats':no_of_chats,
                'retrieved_commented':retrieved_commented,
                'form':form
            }
            if request.method=='POST':
                    form = Overviewform(request.POST, request.FILES)

                    form.fields['subject'].initial=subject_object.id
                    form.fields['class_n'].initial=class_object.id
                    form.fields['teacher'].initial=teacher_id
                    form.fields['subject'].value=subject_object.id
                    form.fields['class_n'].value=class_object.id
                    form.fields['teacher'].value=teacher_id.id
                    #overview_value = form.cleaned_data.get('overview')
                    save_form = form.save(commit=False)
                    form.cleaned_data.get('over_view')
                    form.cleaned_data.get('teacher')
                    form.cleaned_data.get('class_n')
                    form.cleaned_data.get('subject')
                    form.cleaned_data.get('duration')
                    form.cleaned_data.get('price')
                    save_form.image= request.FILES['image']
                    file_type = save_form.image.url.split('.')[-1]
                    file_type = file_type.lower()
                    if file_type not in IMAGE_FILE_TYPES:
                        messages.warning(request, 'Please check the image you uploaded')
                        return render(request, 'error.html')
                    # else:
                    #     print('image in')
                    try:
                        save_form.video= request.FILES['video']
                        file_type2 = save_form.video.url.split('.')[-1]
                        file_type2 = file_type2.lower()
                        if file_type2 not in VID_FILE_TYPES:
                            messages.warning(request, 'Please check the video you uploaded')
                            return render(request, 'error.html')
                    except:
                        pass
                    save_form.save()
                    print('done_saving')
                    messages.info(request, "Overview successfully added,now continue to the class")
                    return redirect('e_learning:teacher_homepage')
            return render(request,'overview.html',context)
    except NameError:
        return redirect('e_learning:teacher_homepage')
            ########################


@login_required
def upload_content(request):
    content=Content.objects.all().order_by('-id')
    form = Contentform()
    context = {"form": form,"content":content}
    if request.method == 'POST':
        form = Contentform(request.POST, request.FILES)
        if form.is_valid():
            topic = form.cleaned_data.get("topic")
            subject= form.cleaned_data.get("subject")
            class_level= form.cleaned_data.get("class_level")
            content= form.cleaned_data.get("content")
            notes = form.cleaned_data.get("notes")
            video= form.cleaned_data.get("video")
            content_form = Content(
                    user=request.user,
                    topic=topic,
                    subject=subject,
                    class_level=class_level,
                    content=content,
                    notes=notes,
                    video=video

                )
            content_form.save()
            #user_pr = form.save(commit=False)
            #user_pr.save()
            messages.info(request, "Topic was added.")
            return redirect('e_learning:view_new_uploaded_content')
            print("saved")
        else:
            messages.info(request, "something went wrong.")
            print('didnt save')
	    #return redirect('e_learning:upload_content')

	#return render(request,'index.html', context)
    return render(request,'upload_content.html',context)

def pdf_view(request):
    try:
        return FileResponse(open('{{ object.notes.url }}', 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()

@login_required
def post_subject(request):

    form = Contentform()
    if request.method == 'POST':
        form = Contentform(request.POST, request.FILES)
        if form.is_valid():
            user_pr = form.save(commit=False)
            #user_pr.image = request.FILES['image']
            #file_type = user_pr.image.url.split('.')[-1]
            #file_type = file_type.lower()
            #if file_type not in IMAGE_FILE_TYPES:
            #    return render(request, 'shop/error.html')
            user_pr.save()
            return render(request, 'shop/product2.html', {'user_pr': user_pr})
    context = {"form": form,}
    return render(request, 'shop/farmer.html', context)

@login_required
def get_video(request,id):
    obj= Upload_topics.objects.get(id=id)

    subject=Teacher_apply.objects.filter(user=request.user.id)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two
    context= {
        'subject_two':subject_two,
        'subject_one':subject_one,
        'object':obj,
    }
    return render(request, 'video.html', context)

@login_required
def get_document(request,id):
    obj= Content.objects.get(id=id)
    try:
        return FileResponse(open('{{ obj.notes.url }}', 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()
    context = {
        'object':obj,
    }
    return render(request, 'document.html', context)




class HomeView(ListView):
    model = Subjects_overview
    paginate_by = 12
    template_name = 'student_homepage.html'
    # Code block for GET request
    active_user_holder = []
    teacher_holder = []
    all_active_users = User.objects.filter(Q(is_active = True))
    for all_active_user in all_active_users:
        active_user_holder.append(all_active_user)
    new_holder = active_user_holder
    print(new_holder,'new_holder')

    teacher_active=Teacher_apply.objects.filter(user__in = new_holder)
    for all_teacher_active in teacher_active:
        teacher_holder.append(all_teacher_active)
    new_holder2 = teacher_holder
    print(new_holder2,'active_teacher')

    overview=Subjects_overview.objects.filter(teacher__in = new_holder2)   
    # for i in overview:
    #     print(i.price,i.teacher.user,i.class_n,i.subject,i.subject.subject_image)
    #     teacher_user=i.teacher.user
    #     profile=UserProfile.objects.filter(user=teacher_user)[0]
    #     print(profile.firstname, profile.lastname)

    def get(self, request, *args, **kwargs):
        context = locals()
        context['overview'] = self.overview


        return render(self.request,self.template_name, context,)

        #print('# Code block for GET request')

    def post(self, request):
        # Code block for POST request
        print('# Code block for POST request')

@login_required
def student_homepage(request):
    student_subjectsz = Subscription.objects.all()
    print(student_subjectsz)
    student_subjects = Subscription.objects.filter(student=request.user.id)
    print(student_subjects)
    for my_course in student_subjects:
        print(my_course.subject)
    context={
        'student_subjects':student_subjects,
    }
    return render(request,'student_personal_homepage.html',context)

@login_required
def student_personal_homepage(request):
    student_subjects = Subscription.objects.filter(student__exact=request.user.id,active__exact=True)
    print(student_subjects)
    for my_course in student_subjects:
        print(my_course.student)
    context={
        'student_subjects':student_subjects,
    }
    return render(request,'student_personal_homepage.html',context)

@login_required
def start_reading(request,slug):
    start_learning=Subscription.objects.get(id=slug)
    material_name = start_learning.subject.subject_name
    material_class = start_learning.class_n
    material_teacher = start_learning.teacher
    material_overview = start_learning.subject_overview
    #container = eval(start_learning.subject.subject_name)
    my_reading_material = Upload_topics.objects.filter(overview = material_overview)
    context ={
    'my_reading_material':my_reading_material,
    'material_name':material_name,
    'material_class':material_class
    }
    return render(request,'start_reading.html',context)

@login_required
def open_content(request,slug):
    open_content=Upload_topics.objects.get(id=slug)
    print(open_content.id)
    slug_vids = open_content.overview.id
    subject_namez=Subjects.objects.get(id = open_content.subject)
    print(subject_namez)
    class_object=Class_table.objects.get(id = open_content.class_level)
    print(class_object)
    template_name = 'open_content.html'
    post = get_object_or_404(Upload_topics, id=open_content.id)
    comments = post.comments.filter(active=True, parent__isnull=True)
    new_comment = None

    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            parent_obj = None
            # get parent comment id from hidden input
            try:
                # id integer e.g. 15
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            # if parent_id has been submitted get parent_obj id
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                # if parent object exist
                if parent_obj:
                    # create replay comment object
                    replay_comment = comment_form.save(commit=False)
                    # assign parent_obj to replay comment
                    replay_comment.parent = parent_obj

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.topic = post
            # Save the comment to the database
            new_comment.save()
            return HttpResponseRedirect(post.get_open_content())
            #return render(reverse('e_learning:open_content',kwargs={'slug':open_content.id}))
    else:

        comment_form = CommentForm(initial={'name': request.user,'user_image':request.user.userprofile.image.url,'email':request.user.userprofile.email})

    return render(request, template_name, {'post': post,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'open_content':open_content,
                                           'slug_vids':slug_vids,
                                           'subject_namez':subject_namez,
                                           'class_object':class_object,
                                           'comment_form': comment_form})

@login_required
def student_video(request,slug_vids):
    student_caller=Subjects_overview.objects.get(id=slug_vids)
    student_videoz = Upload_topics.objects.filter(overview = student_caller)
    context = {
        'student_videoz':student_videoz
    }
    return render(request, 'student_video.html',context)

@login_required
def apply_to_teach(request):
    print(request.user.userprofile,request.user.userprofile.id)
    applyform=Applyform()
    context = {
        'form':applyform

    }


    if request.method=='POST':
        if request.user.userprofile.email != '':
            form = Applyform(request.POST, request.FILES)
            form.fields['user'].initial= request.user
            form.fields['user_profile'].initial= request.user.userprofile
            schools_taught = request.POST.get('schools_taught')
            current_school = request.POST.get('current_school')
            level_of_teaching = request.POST.get('level_of_teaching')
            teacher_registration_id = request.POST.get('teacher_registration_id')
            subject_one = request.POST.get('subject_one')
            subject_two = request.POST.get('subject_two')
            Brief_Self_description = request.POST.get('Brief_Self_description')
            apply_data = Teacher_apply(
                user=request.user,
                user_profile=request.user.userprofile,
                schools_taught=schools_taught,
                current_school=current_school,
                level_of_teaching=level_of_teaching,
                teacher_registration_id=teacher_registration_id,
                subject_one=subject_one,
                subject_two=subject_two,
                Brief_Self_description =Brief_Self_description

            )
            apply_data.save()
            email=request.user.userprofile.email
            name = request.user
            message =f"""
            I want to become a teacher:
            Firstname: {request.user.userprofile.firstname}
            Lastname : {request.user.userprofile.lastname}
            TeacherID: {teacher_registration_id} 
            Email : {request.user.userprofile.email}
            """

            messages.info(request, "Your application has been successfully submitted for review, an e-mail will be sent to verify your account")
            email = EmailMessage(subject= f'{request.user.userprofile.firstname} {request.user.userprofile.lastname} --- Applying to teach',body=message,to=['admin@virtualclass.ug'],                   headers={'Message-ID': name },reply_to=[email])
            email.send()
            return redirect('e_learning:home_view')
        else:
            messages.warning(request, "We've realised you did not provide your email.Please first provide your email in your user profile so that we can get back to you. ----> My Profile")



    return render(request,'apply_to_teach.html',context)

@login_required
def subject_topic(request):
	return render(request,'e_library.html')

@login_required
def e_lib(request):
    active_user_holder = []
    all_active_users = User.objects.filter(Q(is_active = True))
    for all_active_user in all_active_users:
        active_user_holder.append(all_active_user)
    new_holder = active_user_holder
    print(new_holder,'new_holder')
    
    recommended_math_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Mathematics',user__in = new_holder)
    recommended_english_book = Recommend_Subjects_Table.objects.filter(subject_name = 'English',user__in = new_holder)
    recommended_physics_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Physics',user__in = new_holder)
    recommended_chemistry_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Chemistry',user__in = new_holder)
    recommended_biology_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Biology',user__in = new_holder)
    recommended_agric_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Agriculture',user__in = new_holder)
    recommended_geography_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Geography',user__in = new_holder)
    recommended_history_book = Recommend_Subjects_Table.objects.filter(subject_name = 'History',user__in = new_holder)
    recommended_computer_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Computer',user__in = new_holder)
    recommended_lugbara_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Lugbara Ti',user__in = new_holder)
    recommended_art_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Art',user__in = new_holder)
    recommended_french_book = Recommend_Subjects_Table.objects.filter(subject_name = 'French',user__in = new_holder)
    recommended_german_book = Recommend_Subjects_Table.objects.filter(subject_name = 'German')
    recommended_kiswahili_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Kiswahili',user__in = new_holder)
    recommended_chinese_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Chinese',user__in = new_holder)
    recommended_general_paper_book = Recommend_Subjects_Table.objects.filter(subject_name = 'General paper',user__in = new_holder)
    recommended_luganda_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Luganda',user__in = new_holder)
    recommended_Islam_book = Recommend_Subjects_Table.objects.filter(subject_name = 'Islam',user__in = new_holder)

    context={
            'recommended_math_book':recommended_math_book,
            'recommended_english_book':recommended_english_book,
            'recommended_physics_book':recommended_physics_book,
            'recommended_chemistry_book':recommended_chemistry_book,
            'recommended_biology_book':recommended_biology_book,
            'recommended_agric_book':recommended_agric_book,
            'recommended_geography_book':recommended_geography_book,
            'recommended_history_book':recommended_history_book,
            'recommended_computer_book':recommended_computer_book,
            'recommended_lugbara_book':recommended_lugbara_book,
            'recommended_art_book':recommended_art_book,
            'recommended_french_book':recommended_french_book,
            'recommended_german_book':recommended_german_book,
            'recommended_kiswahili_book':recommended_kiswahili_book,
            'recommended_chinese_book':recommended_chinese_book,
            'recommended_general_paper_book':recommended_general_paper_book,
            'recommended_luganda_book':recommended_luganda_book,
            'recommended_Islam_book':recommended_Islam_book,
    }

    return render(request,'e_library.html',context)

def subscription_approval(request,slug):
    overview=Subjects_overview.objects.get(id=slug)
    teacher = Teacher_apply.objects.get(user = overview.teacher.user)
    try:
        overview=Subscription.objects.get(subject_overview__exact=slug,student__exact=request.user)
        overview2=PaymentRecords.objects.get(subject_overview__exact=slug,student__exact=request.user)
        teacher = Teacher_apply.objects.get(user = overview.teacher.user)
        
        #####################3check if payment is successful#############3
        overview2.active=True
        overview2.save()
        overview.active=True
        overview.save()
        
        messages.info(request, "Aready subscribed to this subject")
        return redirect('e_learning:my_subjects')
    except ObjectDoesNotExist:
        apply_data = Subscription(
                student=request.user,
                user_profile=request.user.userprofile,
                subject_overview=overview ,
                class_n= overview.class_n ,
                subject =overview.subject ,
                teacher = teacher,
                Amount = overview.price,
                active = True,
                duration = overview.duration,

            )
        apply_data.save()
        payment = PaymentRecords(
                student=request.user,
                user_profile=request.user.userprofile,
                subject_overview=overview ,
                class_n= overview.class_n ,
                subject =overview.subject ,
                teacher = teacher,
                Amount = overview.price,
                active = True,
                duration = overview.duration,

            )
        payment.save()
        messages.info(request, "You have succefully subscribed to this subject")
        return redirect('e_learning:my_subjects')
    except TypeError:
        #messages.warning(request, "First sign in, or create an account if you do not have one.")
        return redirect('account_login')

#@login_required
def subject_overview(request,slug):
    overview=Subjects_overview.objects.get(id=slug)
    recomend=Subjects_overview.objects.filter(class_n=overview.class_n)
    # for i in recomend:
    #     print(i.price,i.teacher.user,i.class_n,i.subject,i.subject.subject_image)
    recomended = recomend.count()
    # print(recomended)
    #################topics#################
    topic_list=Upload_topics.objects.filter(overview__exact=slug)
    context ={
    'overview':overview,
    'recomend':recomend,
    'recomended':recomended,
    'slug':slug,
    'topic_list':topic_list,
    }
    return render(request,'subject_overview.html',context)


@login_required
def teacher_homepage(request):
    subject=Teacher_apply.objects.filter(user=request.user.id)
    print(request.user)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id
    print(current_teacher,'kkkkkkkk')

    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_chats':no_of_chats,
                'no_of_students':no_of_students,
            }
        return render(request,'teacher_homepage.html',context)
    else:
        counter_list=[]
        retrieved_commented_list=[]
        for my_studnts in list_of_students:
            print(my_studnts)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter,'999000000000')

            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()

            retrieved_commented = retrieve_my_comments[:4]
            retrieved_commented_list.append(retrieved_commented)
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body
        counter_list_no = sum(counter_list)
        context={
            'subject_two':subject_two,
            'subject_one':subject_one,
            'counter':counter_list_no,
            'no_of_students':no_of_students,
            'no_of_chats':no_of_chats,
            'retrieved_commented':retrieved_commented_list[0],
        }
        return render(request,'teacher_homepage.html',context)

@login_required
def teacher_alerts(request,slug):
    topic_handler = []
    subject=Teacher_apply.objects.filter(user=request.user.id)
    print(request.user)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id
    print(current_teacher,'kkkkkkkk')

    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()

        try:
            # topics_id = notification.topic.id
            # topic_handler.append(topics_id)
            # print(topic_handler,'handling')
            # for topic_personal_id in topic_handler:
            open_content=Upload_topics.objects.get(id=slug)
            print(open_content.id)
            subject_namez=Subjects.objects.get(id = open_content.subject)
            print(subject_namez)
            class_object=Class_table.objects.get(id = open_content.class_level)
            print(class_object)
            post = get_object_or_404(Upload_topics, id=slug)
            comments = post.comments.filter(active=True, parent__isnull=True)
            new_comment = None
            template_name = 'teacher_alerts.html'

            # Comment posted
            if request.method == 'POST':
                comment_form = CommentForm(data=request.POST)
                if comment_form.is_valid():
                    parent_obj = None
                    # get parent comment id from hidden input
                    try:
                        # id integer e.g. 15
                        parent_id = int(request.POST.get('parent_id'))
                    except:
                        parent_id = None
                    # if parent_id has been submitted get parent_obj id
                    if parent_id:
                        parent_obj = Comment.objects.get(id=parent_id)
                        # if parent object exist
                        if parent_obj:
                            # create replay comment object
                            replay_comment = comment_form.save(commit=False)
                            # assign parent_obj to replay comment
                            replay_comment.parent = parent_obj

                    # Create Comment object but don't save to database yet
                    new_comment = comment_form.save(commit=False)
                    # Assign the current post to the comment
                    new_comment.topic = post
                    # Save the comment to the database
                    new_comment.save()
                    return HttpResponseRedirect(post.get_teacher_alerts())
            else:

                comment_form = CommentForm(initial={'name': request.user,'user_image':request.user.userprofile.image.url,'email':request.user.userprofile.email})

            return render(request, 'teacher_alerts.html', {
                                                   'subject_two':subject_two,
                                                   'subject_one':subject_one,
                                                   'counter':counter,
                                                   'no_of_students':no_of_students,
                                                   'no_of_chats':no_of_chats,
                                                   'post': post,
                                                   'comments': comment,
                                                   'new_comment': new_comment,
                                                   'comment_form': comment_form}
                                                   )
        except UnboundLocalError:
            messages.info(request, "You donot have any new notifications yet!")
            return redirect('e_learning:teacher_homepage')

    else:
        counter_list=[]
        retrieved_commented_list=[]
        for my_studnts in list_of_students:
            print(my_studnts)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter,'999000000000')

            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()

            retrieved_commented = retrieve_my_comments[:4]
            retrieved_commented_list.append(retrieved_commented)
            print(retrieved_commented)

            for notification in retrieve_my_comments:
                print(notification.topic.id,'66666666666666')

            try:
                # topics_id = notification.topic.id
                # topic_handler.append(topics_id)
                # print(topic_handler,'handling')
                # for topic_personal_id in topic_handler:
                post = get_object_or_404(Upload_topics, id=slug)
                comments = post.comments.filter(active=True, parent__isnull=True)
                new_comment = None

                # Comment posted
                if request.method == 'POST':
                    comment_form = CommentForm(data=request.POST)
                    if comment_form.is_valid():
                        parent_obj = None
                        # get parent comment id from hidden input
                        try:
                            # id integer e.g. 15
                            parent_id = int(request.POST.get('parent_id'))
                        except:
                            parent_id = None
                        # if parent_id has been submitted get parent_obj id
                        if parent_id:
                            parent_obj = Comment.objects.get(id=parent_id)
                            # if parent object exist
                            if parent_obj:
                                # create replay comment object
                                replay_comment = comment_form.save(commit=False)
                                # assign parent_obj to replay comment
                                replay_comment.parent = parent_obj

                        # Create Comment object but don't save to database yet
                        new_comment = comment_form.save(commit=False)
                        # Assign the current post to the comment
                        new_comment.topic = post
                        # Save the comment to the database
                        new_comment.save()
                        return HttpResponseRedirect(post.get_teacher_alerts())
                else:

                    comment_form = CommentForm(initial={'name': request.user,'user_image':request.user.userprofile.image.url,'email':request.user.userprofile.email})
                counter_list_no = sum(counter_list)

                return render(request, 'teacher_alerts.html', {
                                                       'subject_two':subject_two,
                                                       'subject_one':subject_one,
                                                       'counter':counter_list_no,
                                                       'no_of_students':no_of_students,
                                                       'no_of_chats':no_of_chats,
                                                       'retrieved_commented':retrieved_commented_list[0],
                                                       'post': post,
                                                       'comments': comments,
                                                       'new_comment': new_comment,
                                                       'comment_form': comment_form}
                                                       )
            except UnboundLocalError:
                messages.info(request, "You donot have any new notifications yet!")
                return redirect('e_learning:teacher_homepage')

def teacher_comment_topics(request,slug):
    teacher_comment_topic=Subjects_overview.objects.filter(id=slug)
    print(teacher_comment_topic)
    for subject_needed in teacher_comment_topic:
        print(subject_needed.subject.id,'kiiiiiiiiiiiiiiiiiiiiiiiiiii')
    topics_idz = subject_needed.subject.id
    print(topics_idz,'oooooooooooooooooooopppppppppppppppppp')
    materials_class = subject_needed.subject.subject_name
    materials_name = subject_needed.class_n.name

    topic_fields = Upload_topics.objects.filter(subject = topics_idz)
    subject=Teacher_apply.objects.filter(user=request.user.id)
    print(request.user)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id
    print(current_teacher,'kkkkkkkk')
    ########################
    chatrooms = Upload_topics.objects.filter(subject = topics_idz)
    chatroom_list=[]
    chatroom_count_list=[]
    both_dict={}
    for chatroom in chatrooms:
        print(chatroom)
        post = get_object_or_404(Upload_topics, id=chatroom.id)
        #print(post,'??????????????')
        comments = post.comments.filter(active=True, parent__isnull=True)
        #print(comments.count(),'??????????????')
        chatroom_count_list.append(comments.count())
        both_dict[post]=comments.count()

    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'no_of_chats':no_of_chats,
                'topic_fields':topic_fields,
                'both_dict':both_dict,
                'materials_name':materials_name,
                'materials_class':materials_class,
            }
        return render(request,'teacher_comment_topics.html',context)
    else:
        counter_list=[]
        retrieved_commented_list=[]
        for my_studnts in list_of_students:
            print(my_studnts)
            
            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)
            # student_names = UserProfile.objects.filter(user = my_studnt.student.id)
            # for names in student_names:
            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()


            retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
            print(retrieve_my_students)
            for students_retrieved in retrieve_my_students:
                my_student = students_retrieved.student

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter,'999000000000')

            retrieved_commented = retrieve_my_comments[:4]
            retrieved_commented_list.append(retrieved_commented)
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body
        counter_list_no = sum(counter_list)

        context={
            'subject_two':subject_two,
            'subject_one':subject_one,
            'counter':counter_list_no,
            'no_of_chats':no_of_chats,
            'no_of_students':no_of_students,
            'retrieved_commented':retrieved_commented_list[0],
            'teacher_students':teacher_students,
            'topic_fields':topic_fields,
            'both_dict':both_dict,
            'materials_name':materials_name,
            'materials_class':materials_class,
        }
        return render(request,'teacher_comment_topics.html',context)


def teacher_to_alerts(request):
    subject=Teacher_apply.objects.filter(user=request.user.id)
    print(request.user)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id
    print(current_teacher,'kkkkkkkk')


    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()

        teacher_uploaded_subjects=Subjects_overview.objects.filter(teacher=current_teacher)
        print(teacher_uploaded_subjects,'oooooooo')

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'no_of_chats':no_of_chats,
                'counter':counter,
                'no_of_students':no_of_students,
                'teacher_uploaded_subjects':teacher_uploaded_subjects,
            }
        return render(request,'teacher_to_alerts.html',context)
    else:
        counter_list=[]
        for my_studnts in list_of_students:
            print(my_studnts)

            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)
            # student_names = UserProfile.objects.filter(user = my_studnt.student.id)
            # for names in student_names:

            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()

            teacher_uploaded_subjects=Subjects_overview.objects.filter(teacher=current_teacher)
            print(teacher_uploaded_subjects,'oooooooo')

            retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
            print(retrieve_my_students)
            for students_retrieved in retrieve_my_students:
                my_student = students_retrieved.student

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter,'999000000000')

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body
        counter_list_no = sum(counter_list)

        context={
            'subject_two':subject_two,
            'subject_one':subject_one,
            'counter':counter_list_no,
            'no_of_students':no_of_students,
            'no_of_chats':no_of_chats,
            'retrieved_commented':retrieved_commented,
            'teacher_students':teacher_students,
            'teacher_uploaded_subjects':teacher_uploaded_subjects,
        }
        return render(request,'teacher_to_alerts.html',context)

def about(request):
	return render(request,'about.html')

def group_discussion(request):
    subject_discussion = Subjects.objects.all()
    chatrooms_ = Subjects.objects.all()
    chatroom_list=[]
    chatroom_count_list=[]
    both_dict={}
    c=[1,2]
    for chatroom in chatrooms_:
        #print(chatroom.id,'ppppppppppppppppppppp')
        post = get_object_or_404(Subjects, id=chatroom.id)
        #print(post,'??????????????')
        comments = post.comments.filter(active=True, parent__isnull=True)
        #print(comments.count(),'??????????????')
        chatroom_count_list.append(comments.count())
        both_dict[post.subject_name]=comments.count()

    context={
        'subject_discussion':subject_discussion,
        'both_dict':both_dict
        }
    return render(request,'group_discussion.html',context)

@login_required
def start_discussion(request,slug):
    subject_discuss = Subjects.objects.get(id = slug)
    subject_to_discuss = subject_discuss.subject_name
    template_name = 'start_discussion.html'
    post = get_object_or_404(Subjects, id=subject_discuss.id)
    comments = post.comments.filter(active=True, parent__isnull=True)
    new_comment = None

    # Comment posted
    if request.method == 'POST':
        comment_form = StudentChatCommentForm(data=request.POST)
        if comment_form.is_valid():
            parent_obj = None
            # get parent comment id from hidden input
            try:
                # id integer e.g. 15
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            # if parent_id has been submitted get parent_obj id
            if parent_id:
                parent_obj = StudentChatComment.objects.get(id=parent_id)
                # if parent object exist
                if parent_obj:
                    # create replay comment object
                    replay_comment = comment_form.save(commit=False)
                    # assign parent_obj to replay comment
                    replay_comment.parent = parent_obj

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.topic = post
            # Save the comment to the database
            new_comment.save()
            return HttpResponseRedirect(post.get_start_discussion_url())
            #return render(reverse('e_learning:open_content',kwargs={'slug':open_content.id}))
    else:

        comment_form = CommentForm(initial={'name': request.user,'user_image':request.user.userprofile.image.url,'email':request.user.userprofile.email})

    return render(request, template_name, {'post': post,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'subject_to_discuss':subject_to_discuss,
                                           'comment_form': comment_form})

@login_required
def error_404_view(request,exception):
	return render(request,'error.html')

@login_required
def teacher_new_base(request):
	return render(request,'teacher_new_base.html')

@login_required
def view_my_students(request):
    subject=Teacher_apply.objects.filter(user=request.user.id)
    print(request.user)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id
    print(current_teacher,'kkkkkkkk')

    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'no_of_chats':no_of_chats,
            }
        return render(request,'view_my_students.html',context)
    else:
        counter_list=[]
        retrieved_commented_list=[]
        for my_studnts in list_of_students:
            print(my_studnts)
            
            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter,'999000000000')

            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()
    

            retrieved_commented = retrieve_my_comments[:4]
            retrieved_commented_list.append(retrieved_commented)
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body
        counter_list_no = sum(counter_list)
        context={
            'subject_two':subject_two,
            'subject_one':subject_one,
            'counter':counter_list_no,
            'no_of_students':no_of_students,
            'no_of_chats':no_of_chats,
            'retrieved_commented':retrieved_commented_list[0],
            'teacher_students':teacher_students

        }
        return render(request,'view_my_students.html',context)
        #####################

@login_required
def my_uploaded(request,slug):
    uploaded=Subjects_overview.objects.get(id=slug)
    print(slug)
    Subjects_overview.objects.get(id=slug).delete()
    try:
        Upload_topics.objects.get(id=slug).delete()
    except ObjectDoesNotExist :
        pass
    #########Delete item from here##############
    messages.info(request, "Subject s deleted")
    return redirect('e_learning:my_uploaded_subjects')

IMAGE_FILE_TYPES3 = ['png', 'jpg', 'jpeg']
VID_FILE_TYPES = ['mp4']
@login_required
def edit_my_uploaded(request,slug):
    p = re.compile('([^\W]+)')
    form = Overviewform()
    subject=Teacher_apply.objects.filter(user=request.user.id)
    print(request.user)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id
    print(current_teacher,'kkkkkkkk')

    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()
        form = Overviewform(initial={'over_view': uploaded.over_view,'image':uploaded.image,'video':uploaded.video,'duration':uploaded.duration,'price':uploaded.price,'subject':uploaded.subject,"class_n":uploaded.class_n,'teacher':uploaded.teacher})
        if request.method=='POST':
            if form.is_valid:
                form = Overviewform(request.POST, request.FILES)
                duration_update =request.POST.get('duration')
                # uploaded.subject =request.POST.get('subject')
                # uploaded.class_n =request.POST.get('class_n')
                # uploaded.teacher =request.POST.get('teacher')
                uploaded.over_view =request.POST.get('over_view')
                uploaded.save()
                try:
                    splits=p.findall(f"{request.POST.get('duration')}")
                    uploaded.duration =datetime.timedelta(days=int(splits[0]),hours=int(splits[1]),minutes=int(splits[2]),seconds=int(splits[3]))
                    uploaded.save()
                except:
                    pass
                uploaded.price =request.POST.get('price')
                uploaded.save()
                if request.FILES.get('image')==None:
                    pass
                else:
                    uploaded.image = request.FILES.get('image')
                    file_type = uploaded.image.url.split('.')[-1]
                    file_type = file_type.lower()
                    if file_type not in IMAGE_FILE_TYPES3:
                        messages.warning(request, 'Please check the image you uploaded')
                        return render(request, 'error.html')
                    else:
                        uploaded.save()

                if request.FILES.get('video')== None:
                    pass
                else:
                    uploaded.video= request.FILES.get('video')
                    file_type = uploaded.video.url.split('.')[-1]
                    file_type = file_type.lower()
                    if file_type not in VID_FILE_TYPES:
                        messages.warning(request, 'Please check the video you uploaded')
                        return render(request, 'error.html')
                    else:
                        uploaded.save()
                print('done_saving')
                messages.info(request, "Topic successfully updated")
                return redirect('e_learning:my_uploaded_subjects')
            else:
                messages.warning(request, "please fill all feilds")



        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_chats':no_of_chats,
                'no_of_students':no_of_students,
                'form':form,
            }
        return render(request,'teacher_edit_subject_topics.html',context)
    else:
        for my_studnts in list_of_students:
            print(my_studnts)

            uploaded=Subjects_overview.objects.get(id=slug)
            print(slug)
            print(uploaded.subject.id)
            uplo = (uploaded.class_n.id,uploaded.class_n)
            print(uplo)
            edit_uploaded=Upload_topics.objects.filter(subject__exact=uploaded.subject.id,class_level__exact=uploaded.class_n.id)
            print(edit_uploaded)

            subject_name = uploaded.subject

            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            #print(counter,'999000000000')

            retrieved_commented = retrieve_my_comments[:4]
            #print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body
            form = Overviewform(initial={'over_view': uploaded.over_view,'image':uploaded.image,'video':uploaded.video,'duration':uploaded.duration,'price':uploaded.price,'subject':uploaded.subject,"class_n":uploaded.class_n,'teacher':uploaded.teacher})
            if request.method=='POST':
                if form.is_valid:
                    form = Overviewform(request.POST, request.FILES)
                    duration_update =request.POST.get('duration')
                    # uploaded.subject =request.POST.get('subject')
                    # uploaded.class_n =request.POST.get('class_n')
                    # uploaded.teacher =request.POST.get('teacher')
                    uploaded.over_view =request.POST.get('over_view')
                    uploaded.save()
                    
                    try:
                        splits=p.findall(f"{request.POST.get('duration')}")
                        uploaded.duration =datetime.timedelta(days=int(splits[0]),hours=int(splits[1]),minutes=int(splits[2]),seconds=int(splits[3]))
                        uploaded.save()
                    except:
                        pass
                    
                    uploaded.price =request.POST.get('price')
                    uploaded.save()
                    if request.FILES.get('image')==None:
                        pass
                    else:
                        uploaded.image = request.FILES.get('image')
                        file_type = uploaded.image.url.split('.')[-1]
                        file_type = file_type.lower()
                        if file_type not in IMAGE_FILE_TYPES3:
                            messages.warning(request, 'Please check the image you uploaded')
                            return render(request, 'error.html')
                        else:
                            uploaded.save()

                    if request.FILES.get('video')== None:
                        pass
                    else:
                        uploaded.video= request.FILES.get('video')
                        file_type = uploaded.video.url.split('.')[-1]
                        file_type = file_type.lower()
                        if file_type not in VID_FILE_TYPES:
                            messages.warning(request, 'Please check the video you uploaded')
                            return render(request, 'error.html')
                        else:
                            uploaded.save()
                    print('done_saving')
                    messages.info(request, "Topic successfully updated")
                    return redirect('e_learning:my_uploaded_subjects')
                else:
                    messages.warning(request, "please fill all feilds")
            

            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'retrieved_commented':retrieved_commented,
                'uploaded':uploaded,
                'no_of_chats':no_of_chats,
                'edit_uploaded':edit_uploaded,
                'subject_name':subject_name,
                'form':form,
            }
            return render(request,'teacher_edit_subject_topics.html',context)

@login_required
def topic_delete(request,slug):
    Upload_topics.objects.get(id=slug).delete()
    # context={

    # }
    messages.info(request, "Topic successfully deleted")
    return redirect('e_learning:my_uploaded_subjects')

@login_required
def edit_my_topic(request,slug):
    form = Uploadform()
    subject=Teacher_apply.objects.filter(user=request.user.id)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two
    # uploaded=Subjects_overview.objects.get(id=slug)
    # print(slug)
    #print(uploaded.subject.id)
    #item6=Item.objects.filter(category=obj.category)
    edit_uploaded=Upload_topics.objects.get(id=slug)
    print(edit_uploaded,edit_uploaded.topic,'--------------')
    form = Uploadform(initial={'overview': edit_uploaded.overview,'topic':edit_uploaded.topic,'teacher':edit_uploaded.teacher,'class_level':edit_uploaded.class_level,'subject':edit_uploaded.subject,'content':edit_uploaded.content,'attached_file':edit_uploaded.attached_file,'videos':edit_uploaded.videos})

    if request.method=='POST':
        form = Uploadform(request.POST, request.FILES)
        # edit_uploaded.overview = eval(request.POST.get('overview'))

        # edit_uploaded.teacher = request.POST.get('teacher')
        # print(teacher)
        edit_uploaded.content =request.POST.get('content')
        #print(content)
        edit_uploaded.class_level =request.POST.get('class_level')
        #print(class_level)
        # edit_uploaded.subject = request.POST.get('subject')
        # print(subject)
        if request.FILES.get('attached_file')!=None:
            edit_uploaded.attached_file = request.FILES.get('attached_file')
            file_type = edit_uploaded.attached_file.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in DOC_FILE_TYPES:
                messages.warning(request, 'Please check the document you uploaded')
                return render(request, 'error.html')
            else:
                edit_uploaded.save()
        if request.FILES.get('videos')!=None:
            edit_uploaded.videos= request.FILES.get('videos')
            file_type = edit_uploaded.videos.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in VID_FILE_TYPES:
                messages.warning(request, 'Please check the video you uploaded')
                return render(request, 'error.html')
            else:
                edit_uploaded.save()
        #attached_file = request.FILES['attached_file']
        # print(attached_file)
        # videos = request.FILES['videos']
        # print(videos)
        edit_uploaded.save()
        print('done_saving')
        messages.info(request, "Topic successfully updated")


    context={
        'edit_uploaded':edit_uploaded,
        'subject_two':subject_two,
        'subject_one':subject_one,
        'form':form
    }
    return render(request,'teacher_edit_subject_individual_topics.html',context)
#######kam and edit here
@login_required
def teacher_uploaded_subjects(request):
    subject=Teacher_apply.objects.filter(user=request.user.id)
    print(request.user)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id
    print(current_teacher,'kkkkkkkk')

    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_chats':no_of_chats,
                'no_of_students':no_of_students,
            }
        return render(request,'teacher_uploaded_subjects.html',context)
    else:
        counter_list=[]
        retrieved_commented_list=[]
        for my_studnts in list_of_students:
            print(my_studnts)
            
            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter,'999000000000')

            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()

            teacher_uploaded_subject=Subjects_overview.objects.filter(teacher=current_teacher)
            retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
            print(retrieve_my_students)
            for students_retrieved in retrieve_my_students:
                my_student = students_retrieved.student

            retrieved_commented = retrieve_my_comments[:4]
            retrieved_commented_list.append(retrieved_commented)
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body
        counter_list_no = sum(counter_list)
        context={
            'subject_two':subject_two,
            'subject_one':subject_one,
            'counter':counter_list_no,
            'no_of_students':no_of_students,
            'no_of_chats':no_of_chats,
            'retrieved_commented':retrieved_commented_list[0],
            'teacher_students':teacher_students,
            'teacher_uploaded_subject':teacher_uploaded_subject,
        }
        return render(request,'teacher_uploaded_subjects.html',context)
        

@login_required
def transaction_details(request):
    subject=Teacher_apply.objects.filter(user=request.user.id)
    print(request.user)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id
    print(current_teacher,'kkkkkkkk')

    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_chats':no_of_chats,
                'no_of_students':no_of_students,
            }
        return render(request,'transaction_details.html',context)
    else:
        counter_list=[]
        retrieved_commented_list=[]
        for my_studnts in list_of_students:
            print(my_studnts)
            
            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter,'999000000000')

            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()

            retrieved_commented = retrieve_my_comments[:4]
            retrieved_commented_list.append(retrieved_commented)
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body
        counter_list_no = sum(counter_list)
        context={
            'subject_two':subject_two,
            'subject_one':subject_one,
            'counter':counter_list_no,
            'no_of_students':no_of_students,
            'no_of_chats':no_of_chats,
            'retrieved_commented':retrieved_commented_list[0],
        }
        return render(request,'transaction_details.html',context)
        ###################


@login_required
def e_books(request):
    subject=Teacher_apply.objects.filter(user=request.user.id)
    print(request.user)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id
    print(current_teacher,'kkkkkkkk')

    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()

        recommend_one = Recommend_Subjects_Table.objects.filter(subject_name__exact=subject_one)
        recommend_two = Recommend_Subjects_Table.objects.filter(subject_name__exact=subject_two)

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_chats':no_of_chats,
                'no_of_students':no_of_students,
                'recommend_one':recommend_one,
                'recommend_two':recommend_two
            }
        return render(request,'e_books.html',context)
    else:
        counter_list=[]
        for my_studnts in list_of_students:
            print(my_studnts)
            
            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter,'999000000000')

            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()
            recommend_one = Recommend_Subjects_Table.objects.filter(subject_name__exact=subject_one)
            recommend_two = Recommend_Subjects_Table.objects.filter(subject_name__exact=subject_two)

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body
        counter_list_no = sum(counter_list)
        context={
            'subject_two':subject_two,
            'subject_one':subject_one,
            'counter':counter_list_no,
            'no_of_students':no_of_students,
            'no_of_chats':no_of_chats,
            'retrieved_commented':retrieved_commented,
            'recommend_one':recommend_one,
            'recommend_two':recommend_two
        }
        return render(request,'e_books.html',context)
        ################


IMAGE_FILE_TYPES4 = ['png', 'jpg', 'jpeg']
@login_required
def recommend_book(request):
     if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        class_level = request.POST.get('class_level')
        book_title = request.POST.get('book_title')
        book_cover_image = request.FILES.get('book_cover_image')
        attach_book = request.FILES.get('attach_book')
        recommended_by = request.POST.get('recommended_by')
        recommend_form = Recommend_Subjects_Table(
                    user = request.user,
                    subject_name=subject_name,
                    class_level=class_level,
                    book_title=book_title,
                    book_cover_image=book_cover_image,
                    attach_book=attach_book,
                    recommended_by=recommended_by,
                        )
        recommend_form.save()
        messages.info(request, "A New Book Has Been Recommended")
        return redirect('e_learning:e_books')

@login_required
def Search_book(request):
    if ('dd' in request.GET) and request.GET['dd'].strip():
        query_string = request.GET.get('dd')
        print(query_string)
        over_view = Recommend_Subjects_Table.objects.filter(subject_name__icontains = query_string)|Recommend_Subjects_Table.objects.filter(book_title__icontains = query_string)
        context = {
            'over_view': over_view,
            'query' : query_string,      
        }
        return render(request,'search_book_.html',context)
    else:
        over_view = None
        query_string = request.GET.get('dd')
        context = {
            'over_view': over_view,
            'query' : query_string,      
        }
        return render(request,'search_book_.html',context)


def FAQ(request):
	return render(request,'FAQ.html')

def privacy(request):
	return render(request,'privacy.html')

# def my_profile(request):
# 	return render(request,'my_profile.html')

@login_required
def payment_details(request):
    my_pay_records=PaymentRecords.objects.filter(student=request.user.id)
    print(my_pay_records)
    context = {
            'my_pay_records':my_pay_records,
    }
    return render(request,'student_payment_details.html',context)

@login_required
def switch_to_teacher_page(request):
    subject=Teacher_apply.objects.filter(user=request.user.id)
    subjects=[]
    for sub in subject:
        subjects.append(sub.subject_one)
        subjects.append(sub.subject_two)

    context= {
        'subjects':subjects,
    }
    return render(request,'teacher_homepage.html',context)

@login_required
def view_new_uploaded_content(request):
    content=Content.objects.all().order_by('-id')
    subject=Teacher_apply.objects.filter(user=request.user.id)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    print(retrieve_my_students)
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student

    retrieve_my_comments = Comment.objects.filter(name__exact=my_student,parent__exact = None)
    counter = retrieve_my_comments.count()

    retrieved_commented = retrieve_my_comments[:4]
    print(retrieved_commented)

    for notification in retrieved_commented:
        notifications = notification.body

    context= {
        'subject_two':subject_two,
        'subject_one':subject_one,
        'counter':counter,
        'retrieved_commented':retrieved_commented,
        "content":content
        }
    return render(request,'view_new_uploaded_content.html',context)


# class MyFormView(View):
#     form_class = Contentform
#     initial = {'key': 'value'}
#     template_name = 'index.html'

#     def get(self, request, *args, **kwargs):
#         form = self.form_class(initial=self.initial)
#         return render(request, self.template_name, {'form': form})

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             # <process form cleaned data>
#             return HttpResponseRedirect('/')

#         return render(request, self.template_name, {'form': form})

@login_required
def classes(request):
    subject=Teacher_apply.objects.filter(user=request.user.id)
    class_s=Class_table.objects.all()
    subjects=[]
    for sub in subject:
        subjects.append(sub.subject_one)
        subjects.append(sub.subject_two)
        print(sub.subject_one,sub.subject_two)
    print(subjects)
    #print(subject[0].subject_one.id,subject[0].subject_two.id)
    subject_o=subject[0]
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two
    subject_id=Subjects.objects.get(subject_name=subject[0].subject_one)

    #print(subject_id.id)
    subject_id = subject_id.id

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id

    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()

        context={
                'subject_two':subject_two,
                'subject':subject,
                'subjects':subjects,
                'counter':counter,
                'subject_one':subject_one,
                'no_of_chats':no_of_chats,
                'subject_id':subject_id,
                'subject_o':subject_o,
                'class_s':class_s,
                'no_of_students':no_of_students,
            }
        return render(request,'classes.html',context)
    else:
        counter_list=[]
        for my_studnts in list_of_students:
            print(my_studnts)
            
            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter,'999000000000')

            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body
        counter_list_no = sum(counter_list)
        context={
            'subject_two':subject_two,
            'subject_one':subject_one,
            'subject_id':subject_id,
            'subject_o':subject_o,
            'subject':subject,
            'subjects':subjects,
            'class_s':class_s,
            'no_of_students':no_of_students,
            'no_of_students':no_of_students,
            'no_of_chats':no_of_chats,
            'counter':counter_list_no,
            'retrieved_commented':retrieved_commented,

        }
        return render(request,'classes.html',context)
        ################
        # for my_studnts in list_of_students:
        #     print(my_studnts)

        #     retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
        #     counter = retrieve_my_comments.count()
        #     print(counter,'999000000000')

        #     no_of_chats = Chat.objects.filter(members= request.user.id)
        #     no_of_chats = no_of_chats.count()

        #     retrieved_commented = retrieve_my_comments[:4]
        #     print(retrieved_commented)

        #     for notification in retrieved_commented:
        #         notifications = notification.body

        #     context={
        #         'subject_two':subject_two,
        #         'subject':subject,
        #         'subjects':subjects,
        #         'counter':counter,
        #         'retrieved_commented':retrieved_commented,
        #         'subject_one':subject_one,
        #         'no_of_chats':no_of_chats,
        #         'subject_id':subject_id,
        #         'subject_o':subject_o,
        #         'class_s':class_s,
        #         'no_of_students':no_of_students,
        #     }
        #     return render(request,'classes.html',context)

@login_required
def classes_base(request):
    subject=Teacher_apply.objects.filter(user=request.user.id)
    class_s=Class_table.objects.all()

    subjects=[]
    for sub in subject:
        subjects.append(sub.subject_one)
        subjects.append(sub.subject_two)

    print(subjects)
    #print(subject[0].subject_one.id,subject[0].subject_two.id)
    subject_o=subject[0]
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two
    subject_id=Subjects.objects.get(subject_name=subject[0].subject_one)
    #print(subject_id.id)
    subject_id = subject_id.id
    for i in class_s:
        print(i.id)

    context = {
        'subject_two':subject_two,
        'subject':subject,
        'subjects':subjects,
        'subject_one':subject_one,
        'subject_id':subject_id,
        'subject_o':subject_o,
        'class_s':class_s
    }
    #print(class_s.value)
    return render(request,'teacher_base.html',context)

@login_required
def classes2(request):
    subject=Teacher_apply.objects.filter(user=request.user.id)
    class_s=Class_table.objects.all()

    #print(subject[0].subject_one.id,subject[0].subject_two.id)
    subject_o=subject[0]
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two
    subject_id=Subjects.objects.get(subject_name=subject[0].subject_two)
    print(subject_id.id,"***********")
    subject_id = subject_id.id
    print(class_s)

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = (my_teacher_id.id)
    print(current_teacher,'kkkkkkkk')

    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'subject_id':subject_id,
                'no_of_chats':no_of_chats,
                'subject_o':subject_o,
                'class_s':class_s,
                'no_of_students':no_of_students,
            }
        return render(request,'classes.html',context)
    else:
        counter_list=[]
        for my_studnts in list_of_students:
            print(my_studnts)
            
            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter,'999000000000')

            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body
        counter_list_no = sum(counter_list)
        context={
            'subject_two':subject_two,
            'subject_one':subject_one,
            'subject_id':subject_id,
            'subject_o':subject_o,
            'subject':subject,
            'class_s':class_s,
            'no_of_students':no_of_students,
            'no_of_students':no_of_students,
            'no_of_chats':no_of_chats,
            'counter':counter_list_no,
            'retrieved_commented':retrieved_commented,

        }
        return render(request,'classes.html',context)


def terms_and_conditions(request):
    return render(request,'terms_and_conditions.html')

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('your_name')
        phone_no = request.POST.get('phone_no')
        email = request.POST.get('email')
        message = request.POST.get('message')
        try:
            # admin@virtualclass.ug
            email = EmailMessage(subject= f'Inquiry from {name}',body=message,to=['admin@virtualclass.ug'],headers={'Message-ID': name,'Contact':phone_no },reply_to=[email])
            email.send()
            
            # send_mail(name, phone_no, email,message, ['capstoneprojects2020@gmail.com'])
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        # return redirect('success')
        messages.info(request, " We have received your inquiry, we shall get back to you as soon as possible.")
        return redirect('e_learning:contact_us')
    return render(request,'contact_us.html')

def team(request):
    return render(request,'team.html')

def about_us(request):
    return render(request,'about_us.html')

def comment(request):
    return render(request,'comment.html')

@login_required
def chatroom(request):
    comment_form=CommentForm()
    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id

    check_my_subjects = Subscription.objects.filter(student__exact=request.user.id) | Subscription.objects.filter(teacher__exact = current_teacher)
    print(check_my_subjects)

    for check_subjects in check_my_subjects:
        print(check_subjects)

    needed_id = check_subjects.id

    template_name = 'chatroom.html'
    # post = Upload_topics.objects.filter(subject=needed_id,class_level__exact=check_subjects.class_n.id)
    # print(post)
    comments = post.comments.filter(active=True, parent__isnull=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            parent_obj = None
            # get parent comment id from hidden input
            try:
                # id integer e.g. 15
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            # if parent_id has been submitted get parent_obj id
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                # if parent object exist
                if parent_obj:
                    # create replay comment object
                    replay_comment = comment_form.save(commit=False)
                    # assign parent_obj to replay comment
                    replay_comment.parent = parent_obj

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.topic = post
            # Save the comment to the database
            new_comment.save()
            return redirect('e_learning:post_detail')

    context = {
        'comment_form':comment_form,
        'check_my_subjects':check_my_subjects

    }

    return render(request,'chatroom.html',context)

@login_required
def push(request,slug):
    print(slug)
    # if request.method=='POST':
    #     subject_id=request.POST.get("subject_id")
    #     print(subject_id)

    context = {
    }
    return render(request,'classes.html',context)

##########################views
@login_required
def post_detail(request):
    template_name = 'post_detail.html'
    post = get_object_or_404(Upload_topics, id=1)
    comments = post.comments.filter(active=True, parent__isnull=True)
    new_comment = None

    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            parent_obj = None
            # get parent comment id from hidden input
            try:
                # id integer e.g. 15
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            # if parent_id has been submitted get parent_obj id
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                # if parent object exist
                if parent_obj:
                    # create replay comment object
                    replay_comment = comment_form.save(commit=False)
                    # assign parent_obj to replay comment
                    replay_comment.parent = parent_obj

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.topic = post
            # Save the comment to the database
            new_comment.save()
            return redirect('e_learning:post_detail')
    else:

        comment_form = CommentForm(initial={'name': request.user,'user_image':request.user.userprofile.image.url,'email':request.user.userprofile.email})

    return render(request, template_name, {'post': post,
                                          'comments': comments,
                                          'new_comment': new_comment,
                                          'comment_form': comment_form})

@login_required
#########view.py###########
def chatroom(request):
    comment_form=CommentForm()
    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id

    check_my_subjects = Subscription.objects.filter(student__exact=request.user.id) | Subscription.objects.filter(teacher__exact = current_teacher)
    print(check_my_subjects)

    for check_subjects in check_my_subjects:
        print(check_subjects)

    needed_id = check_subjects.id

    template_name = 'chatroom.html'
    # post = Upload_topics.objects.filter(subject=needed_id,class_level__exact=check_subjects.class_n.id)
    # print(post)
    comments = post.comments.filter(active=True, parent__isnull=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            parent_obj = None
            # get parent comment id from hidden input
            try:
                # id integer e.g. 15
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            # if parent_id has been submitted get parent_obj id
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                # if parent object exist
                if parent_obj:
                    # create replay comment object
                    replay_comment = comment_form.save(commit=False)
                    # assign parent_obj to replay comment
                    replay_comment.parent = parent_obj

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.topic = post
            # Save the comment to the database
            new_comment.save()
            return redirect('e_learning:post_detail')

    context = {
        'comment_form':comment_form,
        'check_my_subjects':check_my_subjects

    }

    return render(request,'chatroom.html',context)

def push(request,slug):
    print(slug)
    # if request.method=='POST':
    #     subject_id=request.POST.get("subject_id")
    #     print(subject_id)

    context = {
    }
    return render(request,'classes.html',context)

##########################views
def post_detail(request):
    template_name = 'post_detail.html'
    post = get_object_or_404(Upload_topics, id=1)
    comments = post.comments.filter(active=True, parent__isnull=True)
    new_comment = None

    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            parent_obj = None
            # get parent comment id from hidden input
            try:
                # id integer e.g. 15
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            # if parent_id has been submitted get parent_obj id
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                # if parent object exist
                if parent_obj:
                    # create replay comment object
                    replay_comment = comment_form.save(commit=False)
                    # assign parent_obj to replay comment
                    replay_comment.parent = parent_obj

            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.topic = post
            # Save the comment to the database
            new_comment.save()
            return redirect('e_learning:post_detail')
    else:

        comment_form = CommentForm(initial={'name': request.user,'user_image':request.user.userprofile.image.url,'email':request.user.userprofile.email})

    return render(request, template_name, {'post': post,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'comment_form': comment_form})

##########choose#########
@login_required
def choose(request):
    subject=Teacher_apply.objects.filter(user=request.user.id)
    print(request.user)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id
    print(current_teacher,'kkkkkkkk')

    list_of_students = []

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    print(list_of_students,'99999999999999999999')

    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0

        form = ChatForm()
        individuals = UserProfile.objects.all()
        print(individuals)

        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()


        if request.method=='POST':
            form = ChatForm(request.POST, request.FILES)
            # form.fields['user'].initial= request.user
            # form.fields['user_profile'].initial= request.user.userprofile


            new=form.save(commit=False)
            new.type = request.POST.get('type')
            new.chat_title = request.POST.get('chat_title')
            new.save()
            form.save_m2m()



            chat_obj=Chat.objects.all().order_by('-id')
            chat_obj_id=chat_obj[0].id
            chat_obj_id2=Chat.objects.get(id=chat_obj_id)
            chat_obj3_id=chat_obj_id2.members.all()
            #print(chat_obj_id2.members.all())
            list_of_chat_partners = []
            for i in chat_obj3_id:
                print(i.user)
                list_of_chat_partners.append(i.user)
            current_user_creating_session = request.user
            print(current_user_creating_session)
            list_of_chat_partners.insert(0,current_user_creating_session)
            new_chat = list_of_chat_partners
            print(new_chat)

            print(chat_obj[0],chat_obj[0].id)
            message=Message(
                chat=chat_obj_id2,
                author=request.user,
                message='welcome'
            )
            message.save()

            return redirect('e_learning:dialogs')

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'no_of_chats':no_of_chats,
                'form':form,
                'individuals':individuals
            }
        return render(request,'choice.html',context)
    else:
        for my_studnts in list_of_students:
            print(my_studnts)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            print(counter,'999000000000')

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()

            for notification in retrieved_commented:
                notifications = notification.body

            form = ChatForm()
            individuals = UserProfile.objects.all()


            if request.method=='POST':
                form = ChatForm(request.POST, request.FILES)
                # form.fields['user'].initial= request.user
                # form.fields['user_profile'].initial= request.user.userprofile
                new=form.save(commit=False)
                new.chat_title = request.POST.get('chat_title')
                new.type = request.POST.get('type')
                new.save()
                form.save_m2m()

                chat_obj=Chat.objects.all().order_by('-id')
                chat_obj_id=chat_obj[0].id
                chat_obj_id2=Chat.objects.get(id=chat_obj_id)
                chat_obj3_id=chat_obj_id2.members.all()
                #print(chat_obj_id2.members.all())
                list_of_chat_partners = []
                for i in chat_obj3_id:
                    print(i)
                    #list_of_chat_partners.append(i.user)
                # current_user_creating_session = request.user.username
                # print(current_user_creating_session)
                # list_of_chat_partners.insert(0,current_user_creating_session)
                # new_chat = list_of_chat_partners
                # print(new_chat)

                print(chat_obj[0],chat_obj[0].id)
                message=Message(
                    chat=chat_obj_id2,
                    author=request.user,
                    message='welcome'
                )
                message.save()

                return redirect('e_learning:dialogs')

            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'retrieved_commented':retrieved_commented,
                'no_of_chats':no_of_chats,
                'form': form,
                'individuals' : individuals
            }
            print(individuals)
            return render(request,'choice.html',context)

class DialogsView(View):
    def get(self, request):
        form = ChatRoomForm()
        subject=Teacher_apply.objects.filter(user=request.user.id)
        print(request.user)
        subject_one=subject[0].subject_one
        subject_two=subject[0].subject_two

        #chats
        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()
        chats = ChatRoom.objects.all().order_by('-id')
        #############
        chatrooms = ChatRoom.objects.all()
        chatroom_list=[]
        chatroom_count_list=[]
        both_dict={}
        c=[1,2]
        for chatroom in chatrooms:
            #print(chatroom.id,'ppppppppppppppppppppp')
            post = get_object_or_404(ChatRoom, id=chatroom.id)
            #print(post,'??????????????')
            comments = post.comments.filter(active=True, parent__isnull=True)
            #print(comments.count(),'??????????????')
            chatroom_count_list.append(comments.count())
            both_dict[post.title]=comments.count()
        #comments
        list_of_students = []
        my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
        current_teacher = my_teacher_id.id
        retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
        no_of_students = retrieve_my_students.count()
        for students_retrieved in retrieve_my_students:
            my_student = students_retrieved.student
            list_of_students.append(my_student)

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'user_profile': request.user,
                'no_of_chats':no_of_chats,
                'chats':chats,
                'both_dict':both_dict,
                'form': form

            }

        counter_list=[]
        retrieved_commented_list=[]
        for my_studnts in list_of_students:
            print (my_studnts,'uu')
            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter)
            retrieved_commented = retrieve_my_comments[:4]
            retrieved_commented_list.append(retrieved_commented)
            context['retrieved_commented'] = retrieved_commented_list[0]
        print (counter_list,sum(counter_list))
        counter_list_no = sum(counter_list)
        context['counter'] = counter_list_no
        ##################
        return render(request, 'dialogue.html',context)
    def post(self, request):
        form = ChatRoomForm(request.POST, request.FILES)
        user_obj=User.objects.get(id=request.user.id)
        save_data = form.save(commit=False)
        # assign parent_obj to replay comment
        save_data.user_profile = user_obj
        save_data.save()
        return redirect(reverse('e_learning:dialogs'))


class MessagesView(View):
    def get(self, request, chat_id):
        subject=Teacher_apply.objects.filter(user=request.user.id)
        print(request.user)
        subject_one=subject[0].subject_one
        subject_two=subject[0].subject_two
        my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
        current_teacher = my_teacher_id.id
        print(current_teacher,'kkkkkkkk')


        list_of_students = []

        retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
        no_of_students = retrieve_my_students.count()
        for students_retrieved in retrieve_my_students:
            my_student = students_retrieved.student
            list_of_students.append(my_student)
        print(list_of_students,'99999999999999999999')

        if len(list_of_students) == 0:
            counter = 0
            no_of_students = 0
            no_of_chats = ChatRoom.objects.all()
            no_of_chats = no_of_chats.count()

            try:
                chat = Chat.objects.get(id=chat_id)
                print(chat,'bjbjbbj')
                sms = Message.objects.filter(chat=chat_id)
                print(sms)
                if request.user in chat.members.all():
                    chat.message_set.filter(is_readed=False).exclude(author=request.user).update(is_readed=True)
                    print(chat.message_set.filter(is_readed=False).update(is_readed=True))
                    unread=chat.message_set.filter(is_readed=False)
                    print(unread)
                    # for m in unread:
                    #     print(m.is_readed)

                else:
                    print("not a member")
            except Chat.DoesNotExist:
                print('Chat.DoesNotExist')
                #chat = None
            form=MessageForm()
            print(chat,'uuuuuuuuuu')

            return render(
                    request,
                    'message_list.html',
                    {
                        'subject_two':subject_two,
                        'subject_one':subject_one,
                        'counter':counter,
                        'no_of_students':no_of_students,
                        'user_profile': request.user,
                        'no_of_chats':no_of_chats,
                        'chat': chat,
                        'form': form
                    }
                )

        else:
            for my_studnts in list_of_students:
                print(my_studnts)

                retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
                counter = retrieve_my_comments.count()
                print(counter,'999000000000')

                retrieved_commented = retrieve_my_comments[:4]
                print(retrieved_commented)

                no_of_chats = Chat.objects.filter(members= request.user.id)
                no_of_chats = no_of_chats.count()

                for notification in retrieved_commented:
                    notifications = notification.body

                try:
                    chat = Chat.objects.get(id=chat_id)
                    print(chat,'bjbjbbj')
                    sms = Message.objects.filter(chat=chat_id)
                    print(sms)
                    if request.user in chat.members.all():
                        chat.message_set.filter(is_readed=False).exclude(author=request.user).update(is_readed=True)
                        print(chat.message_set.filter(is_readed=False).update(is_readed=True))
                        unread=chat.message_set.filter(is_readed=False)
                        print(unread)
                        # for m in unread:
                        #     print(m.is_readed)

                    else:
                        chat = None
                except Chat.DoesNotExist:
                    chat = None
                form=MessageForm()

                return render(
                        request,
                        'message_list.html',
                        {
                            'subject_two':subject_two,
                            'subject_one':subject_one,
                            'counter':counter,
                            'no_of_chats':no_of_chats,
                            'no_of_students':no_of_students,
                            'retrieved_commented':retrieved_commented,
                            'user_profile': request.user,
                            'chat': chat,
                            'form': form
                        }
                    )

    def post(self, request, chat_id):
        form = MessageForm(data=request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat_id = chat_id
            message.author = request.user
            message.save()
        return redirect(reverse('e_learning:messages', kwargs={'chat_id': chat_id}))

class CreateDialogView(View):
    def get(self, request, user_id):
        subject=Teacher_apply.objects.filter(user=request.user.id)
        print(request.user)
        subject_one=subject[0].subject_one
        subject_two=subject[0].subject_two

        my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
        current_teacher = my_teacher_id.id
        print(current_teacher,'kkkkkkkk')

        list_of_students = []

        retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
        no_of_students = retrieve_my_students.count()
        for students_retrieved in retrieve_my_students:
            my_student = students_retrieved.student
            list_of_students.append(my_student)
        print(list_of_students,'99999999999999999999')

        if len(list_of_students) == 0:
            counter = 0
            no_of_students = 0

            chats = Chat.objects.filter(members__in=[request.user.id, user_id], type=Chat.DIALOG).annotate(c=Count('members')).filter(c=2)
            if chats.count() == 0:
                chat = Chat.objects.create()
                chat.members.add(request.user)
                chat.members.add(user_id)
            else:
                chat = chats.first()


            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'chat_id': chat.id
                }
            return redirect(reverse('e_learning:messages'))
        else:
            for my_studnts in list_of_students:
                print(my_studnts)

                retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
                counter = retrieve_my_comments.count()
                print(counter,'999000000000')

                retrieved_commented = retrieve_my_comments[:4]
                print(retrieved_commented)

                for notification in retrieved_commented:
                    notifications = notification.body

                chats = Chat.objects.filter(members__in=[request.user.id, user_id], type=Chat.DIALOG).annotate(c=Count('members')).filter(c=2)
                if chats.count() == 0:
                    chat = Chat.objects.create()
                    chat.members.add(request.user)
                    chat.members.add(user_id)
                else:
                    chat = chats.first()


                context={
                    'subject_two':subject_two,
                    'subject_one':subject_one,
                    'counter':counter,
                    'no_of_students':no_of_students,
                    'retrieved_commented':retrieved_commented,
                    'chat_id': chat.id
                    }
                return redirect(reverse('e_learning:messages'))

class ApprovalView(View):
    def get(self, request):

        applied = Teacher_apply.objects.filter(user_profile__role="User")
       
        context={
            'applied' :  applied       
        }
        return render(request,'admin/approve.html',context)

class AcceptView(View):
    def get(self,request, user_id):
        got = Teacher_apply.objects.get(id=user_id)
        accepts = UserProfile.objects.get(id= got.user_profile.id)
        accepts.role = "Teacher"
        accepts.save()
        print(accepts)
        try:
            eemail = EmailMessage(subject= 'Request accepted',body= f'Hello {accepts.user.username}, Your account has been approved. You can now upload your content in the selected subjects',to=[accepts.email],
            reply_to=['admin@virtualclass.ug'],headers={'Message-ID': 'Teacher'})
            eemail.send()
            
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        return redirect(reverse('e_learning:approve'))

def declined(request):
    if request.method == 'POST':
        name = request.POST.get('declines')
        email = request.POST.get('starboy')
        try:
            eemail = EmailMessage(subject= 'Request declined',body=name,to=[email],reply_to=['admin@virtualclass.ug'],headers={'Message-ID': 'Try applying again' })
            eemail.send()
            
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        
    return redirect('e_learning:approve')


def conversation(request,slug):
    #subjects
    chat_title = ChatRoom.objects.get(id = slug)
    subject=Teacher_apply.objects.filter(user=request.user.id)
    subject_one=subject[0].subject_one
    subject_two=subject[0].subject_two

    list_of_students = []
    my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
    current_teacher = my_teacher_id.id

    retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
    no_of_students = retrieve_my_students.count()
    for students_retrieved in retrieve_my_students:
        my_student = students_retrieved.student
        list_of_students.append(my_student)
    if len(list_of_students) == 0:
        counter = 0
        no_of_students = 0
        
        #chats
        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()
        #comments
        list_of_students = []
        my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
        current_teacher = my_teacher_id.id
        retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
        no_of_students = retrieve_my_students.count()
        for students_retrieved in retrieve_my_students:
            my_student = students_retrieved.student
            list_of_students.append(my_student)
        
        #form
        comment_form = ChatCommentForm()
        comment_form = ChatCommentForm(initial={
            'name': request.user,
            'user_image':request.user.userprofile.image.url,
            'email':request.user.userprofile.email})
        open_content=ChatRoom.objects.get(id=slug)
        post = get_object_or_404(ChatRoom, id=slug)
        print(post)
        comments = post.comments.filter(active=True, parent__isnull=True)
        new_comment = None
        
        counter_list=[]
        retrieved_commented_list=[]
        context={
            'subject_two':subject_two,
            'subject_one':subject_one,
            'no_of_chats':no_of_chats,
            'comment_form':comment_form,
            'comments':comments,
            'counter':counter,
            'chat_title':chat_title
                        
                        }
        
        for my_studnts in list_of_students:
            print (my_studnts,'uu')
            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter)
            retrieved_commented = retrieve_my_comments[:4]
            retrieved_commented_list.append(retrieved_commented)
            context['retrieved_commented'] = retrieved_commented_list[0]
            print (counter_list,sum(counter_list))
            counter_list_no = sum(counter_list)
            context['counter'] = counter_list_no


        # Comment posted
        if request.method == 'POST':
            comment_form = ChatCommentForm(data=request.POST)
            if comment_form.is_valid():
                parent_obj = None
                # get parent comment id from hidden input
                try:
                    # id integer e.g. 15
                    parent_id = int(request.POST.get('parent_id'))
                except:
                    parent_id = None
                # if parent_id has been submitted get parent_obj id
                if parent_id:
                    parent_obj = ChatComment.objects.get(id=parent_id)
                    # if parent object exist
                    if parent_obj:
                        # create replay comment object
                        replay_comment = comment_form.save(commit=False)
                        # assign parent_obj to replay comment
                        replay_comment.parent = parent_obj

                # Create Comment object but don't save to database yet
                new_comment = comment_form.save(commit=False)
                # Assign the current post to the comment
                new_comment.topic = post
                # Save the comment to the database
                new_comment.save()
                print('saved')
                return HttpResponseRedirect(post.get_chat_url())
        return render(request, 'conversation.html',context)

    ######################
    else:

        #chats
        no_of_chats = ChatRoom.objects.all()
        no_of_chats = no_of_chats.count()
        #comments
        list_of_students = []
        my_teacher_id=Teacher_apply.objects.get(user= request.user.id)
        current_teacher = my_teacher_id.id
        retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
        no_of_students = retrieve_my_students.count()
        for students_retrieved in retrieve_my_students:
            my_student = students_retrieved.student
            list_of_students.append(my_student)
        
        #form
        comment_form = ChatCommentForm()
        comment_form = ChatCommentForm(initial={
            'name': request.user,
            'user_image':request.user.userprofile.image.url,
            'email':request.user.userprofile.email})
        open_content=ChatRoom.objects.get(id=slug)
        post = get_object_or_404(ChatRoom, id=slug)
        print(post)
        comments = post.comments.filter(active=True, parent__isnull=True)
        new_comment = None
        
        counter_list=[]
        retrieved_commented_list=[]
        context={
            'subject_two':subject_two,
            'subject_one':subject_one,
            'no_of_chats':no_of_chats,
            'comment_form':comment_form,
            'comments':comments,
            'chat_title':chat_title
                        
                        }
        for my_studnts in list_of_students:
            print (my_studnts,'uu')
            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            counter_list.append(counter)
            print(counter)
            retrieved_commented = retrieve_my_comments[:4]
            retrieved_commented_list.append(retrieved_commented)
            context['retrieved_commented'] = retrieved_commented_list[0]
            print (counter_list,sum(counter_list))
            counter_list_no = sum(counter_list)
            context['counter'] = counter_list_no


        # Comment posted
        if request.method == 'POST':
            comment_form = ChatCommentForm(data=request.POST)
            if comment_form.is_valid():
                parent_obj = None
                # get parent comment id from hidden input
                try:
                    # id integer e.g. 15
                    parent_id = int(request.POST.get('parent_id'))
                except:
                    parent_id = None
                # if parent_id has been submitted get parent_obj id
                if parent_id:
                    parent_obj = ChatComment.objects.get(id=parent_id)
                    # if parent object exist
                    if parent_obj:
                        # create replay comment object
                        replay_comment = comment_form.save(commit=False)
                        # assign parent_obj to replay comment
                        replay_comment.parent = parent_obj

                # Create Comment object but don't save to database yet
                new_comment = comment_form.save(commit=False)
                # Assign the current post to the comment
                new_comment.topic = post
                # Save the comment to the database
                new_comment.save()
                print('saved')
                return HttpResponseRedirect(post.get_chat_url())
        
        return render(request, 'conversation.html',context)

def charcha_serviceworker(request, js):
    template = get_template('charcha-serviceworker.js')
    html = template.render()
    return HttpResponse(html, content_type="application/x-javascript")