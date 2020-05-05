from django.shortcuts import render, get_object_or_404
from .forms import Overviewform,Uploadform,Applyform,MessageForm,ChatForm
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
#from django.utils import timezone
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.http import FileResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from .forms import CommentForm
from django.core.mail import send_mail,BadHeaderError,EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
    else:
        overview = None

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
        content.save()
        messages.success(request, 'Profile details updated.')
    return render(request,'my_profile.html',context)


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
    #print(teacher_id.id)
    #print(class_id,subject_id,'88888888888888888')
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
                return render(request, 'error.html')
            save_form.video= request.FILES['videos']

            file_type2 = save_form.video.url.split('.')[-1]
            file_type2 = file_type2.lower()
            if file_type2 not in VID_FILE_TYPES:
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

            context={
                     'subject_two':subject_two,
                    'subject_one':subject_one,
                    'counter':counter,
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
                    return render(request, 'error.html')
                # else:
                #     print('image in')
                save_form.video= request.FILES['video']
                file_type2 = save_form.video.url.split('.')[-1]
                file_type2 = file_type2.lower()
                if file_type2 not in VID_FILE_TYPES:
                    return render(request, 'error.html')
                save_form.save()
                print('done_saving')
                messages.info(request, "Overview successfully added,now continue to the class")
                return redirect('e_learning:teacher_homepage')
            return render(request,'overview.html',context)
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

                context={
                    'subject_two':subject_two,
                    'subject_one':subject_one,
                    'counter':counter,
                    'no_of_students':no_of_students,
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
                        return render(request, 'error.html')
                    # else:
                    #     print('image in')
                    save_form.video= request.FILES['video']
                    file_type2 = save_form.video.url.split('.')[-1]
                    file_type2 = file_type2.lower()
                    if file_type2 not in VID_FILE_TYPES:
                        return render(request, 'error.html')
                    save_form.save()
                    print('done_saving')
                    messages.info(request, "Overview successfully added,now continue to the class")
                    return redirect('e_learning:teacher_homepage')

                return render(request,'overview.html',context)
    except NameError:
        return redirect('e_learning:teacher_homepage')

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




class HomeView(LoginRequiredMixin,ListView):
    model = Subjects_overview
    paginate_by = 12
    template_name = 'student_homepage.html'
    # Code block for GET request
    overview=Subjects_overview.objects.all()
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
    #container = eval(start_learning.subject.subject_name)
    my_reading_material = Upload_topics.objects.filter(teacher = material_teacher)
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

        comment_form = CommentForm(initial={'name': request.user,'email':request.user.userprofile.email})

    return render(request, template_name, {'post': post,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'open_content':open_content,
                                           'subject_namez':subject_namez,
                                           'class_object':class_object,
                                           'comment_form': comment_form})

@login_required
def apply_to_teach(request):
    print(request.user.userprofile,request.user.userprofile.id)
    applyform=Applyform()
    context = {
        'form':applyform

    }


    if request.method=='POST':
        form = Applyform(request.POST, request.FILES)
        form.fields['user'].initial= request.user
        form.fields['user_profile'].initial= request.user.userprofile
        schools_taught = request.POST.get('schools_taught')
        current_school = request.POST.get('current_school')
        level_of_teaching = request.POST.get('level_of_teaching')
        subject_one = request.POST.get('subject_one')
        subject_two = request.POST.get('subject_two')
        Brief_Self_description = request.POST.get('Brief_Self_description')
        apply_data = Teacher_apply(
            user=request.user,
            user_profile=request.user.userprofile,
            schools_taught=schools_taught,
            current_school=current_school,
            level_of_teaching=level_of_teaching,
            subject_one=subject_one,
            subject_two=subject_two,
            Brief_Self_description =Brief_Self_description

        )
        apply_data.save()

        messages.info(request, "Your application has succefully submitted for review")
        return redirect('e_learning:home_view')




    return render(request,'apply_to_teach.html',context)

@login_required
def subject_topic(request):
	return render(request,'subject_topic.html')

def subscription_approval(request,slug):
    overview=Subscription.objects.filter(subject_overview=slug)
    #print(overview.active)
    #####################3check if payment is successful#############3
    for subscription_state in overview:
        if subscription_state.active==True:
            messages.info(request, "You have already subscribed to this subject")
            return redirect('e_learning:my_subjects')
        else:
            subscription_state.active=True
            subscription_state.save()
            print(subscription_state.active,'ggggggggg')

            context ={
                    'overview':subscription_state
            }
            messages.info(request, "You have subscribed to this subject")
            return redirect('e_learning:my_subjects')

@login_required
def subject_overview(request,slug):
    overview=Subjects_overview.objects.get(id=slug)
    recomend=Subjects_overview.objects.filter(class_n=overview.class_n)
    teacher = Teacher_apply.objects.get(user = overview.teacher.user)
    for i in recomend:
        print(i.price,i.teacher.user,i.class_n,i.subject,i.subject.subject_image)
    recomended = recomend.count()
    print(recomended)
    context ={
    'overview':overview,
    'recomend':recomend,
    'recomended':recomended,
    'slug':slug,
    }
    try:

        check= Subscription.objects.get(student=request.user,class_n__exact=overview.class_n,subject__exact=overview.subject,teacher=teacher)

    except ObjectDoesNotExist:
        apply_data = Subscription(
                student=request.user,
                user_profile=request.user.userprofile,
                subject_overview=overview ,
                class_n= overview.class_n ,
                subject =overview.subject ,
                teacher = teacher,
                Amount = overview.price,
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
                duration = overview.duration,

            )
        payment.save()

    # if check.exist():
    #     pass
    #     #return render(request,'subject_overview.html',context)
    # else:

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

        no_of_chats = Chat.objects.filter(members= request.user.id)
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
        for my_studnts in list_of_students:
            print(my_studnts)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            print(counter,'999000000000')

            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body

            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'no_of_chats':no_of_chats,
                'retrieved_commented':retrieved_commented,
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

        no_of_chats = Chat.objects.filter(members= request.user.id)
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

                comment_form = CommentForm(initial={'name': request.user,'email':request.user.userprofile.email})

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
        for my_studnts in list_of_students:
            print(my_studnts)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            print(counter,'999000000000')

            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()

            retrieved_commented = retrieve_my_comments[:4]
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

                    comment_form = CommentForm(initial={'name': request.user,'email':request.user.userprofile.email})

                return render(request, 'teacher_alerts.html', {
                                                       'subject_two':subject_two,
                                                       'subject_one':subject_one,
                                                       'counter':counter,
                                                       'no_of_students':no_of_students,
                                                       'no_of_chats':no_of_chats,
                                                       'retrieved_commented':retrieved_commented,
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

        no_of_chats = Chat.objects.filter(members= request.user.id)
        no_of_chats = no_of_chats.count()

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'no_of_chats':no_of_chats,
                'topic_fields':topic_fields,
                'materials_name':materials_name,
                'materials_class':materials_class,
            }
        return render(request,'teacher_comment_topics.html',context)
    else:
        for my_studnts in list_of_students:
            print(my_studnts)

            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)
            # student_names = UserProfile.objects.filter(user = my_studnt.student.id)
            # for names in student_names:
            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()

            retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
            print(retrieve_my_students)
            for students_retrieved in retrieve_my_students:
                my_student = students_retrieved.student

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            print(counter,'999000000000')

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body

            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_chats':no_of_chats,
                'no_of_students':no_of_students,
                'retrieved_commented':retrieved_commented,
                'teacher_students':teacher_students,
                'topic_fields':topic_fields,
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

        no_of_chats = Chat.objects.filter(members= request.user.id)
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
        for my_studnts in list_of_students:
            print(my_studnts)

            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)
            # student_names = UserProfile.objects.filter(user = my_studnt.student.id)
            # for names in student_names:

            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()

            teacher_uploaded_subjects=Subjects_overview.objects.filter(teacher=current_teacher)
            print(teacher_uploaded_subjects,'oooooooo')

            retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
            print(retrieve_my_students)
            for students_retrieved in retrieve_my_students:
                my_student = students_retrieved.student

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            print(counter,'999000000000')

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body

            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'no_of_chats':no_of_chats,
                'retrieved_commented':retrieved_commented,
                'teacher_students':teacher_students,
                'teacher_uploaded_subjects':teacher_uploaded_subjects,
            }
            return render(request,'teacher_to_alerts.html',context)

def about(request):
	return render(request,'about.html')

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

        no_of_chats = Chat.objects.filter(members= request.user.id)
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
        for my_studnts in list_of_students:
            print(my_studnts)

            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)
            # student_names = UserProfile.objects.filter(user = my_studnt.student.id)
            # for names in student_names:
            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()
            retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
            print(retrieve_my_students)
            for students_retrieved in retrieve_my_students:
                my_student = students_retrieved.student

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            print(counter,'999000000000')

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body

            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'retrieved_commented':retrieved_commented,
                'no_of_chats':no_of_chats,
                'teacher_students':teacher_students,
            }
            return render(request,'view_my_students.html',context)

@login_required
def my_uploaded(request,slug):
    uploaded=Subjects_overview.objects.get(id=slug)
    print(slug)
    Subjects_overview.objects.get(id=slug).delete()
    Upload_topics.objects.get(id=slug).delete()
    #########Delete item from here##############
    messages.info(request, "Subject s deleted")
    return redirect('e_learning:my_uploaded_subjects')

@login_required
def edit_my_uploaded(request,slug):
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

        no_of_chats = Chat.objects.filter(members= request.user.id)
        no_of_chats = no_of_chats.count()

        context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_chats':no_of_chats,
                'no_of_students':no_of_students,
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
            print(counter,'999000000000')

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body

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
        edit_uploaded.attached_file = request.FILES.get('attached_file')
        edit_uploaded.videos= request.FILES.get('videos')
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

        no_of_chats = Chat.objects.filter(members= request.user.id)
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
        for my_studnts in list_of_students:
            print(my_studnts)

            teacher_students=Subscription.objects.filter(teacher=current_teacher)
            for my_studnt in teacher_students:
                print(my_studnt,my_studnt.student.id)
            # student_names = UserProfile.objects.filter(user = my_studnt.student.id)
            # for names in student_names:

            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()

            teacher_uploaded_subject=Subjects_overview.objects.filter(teacher=current_teacher)
            print(teacher_uploaded_subject)
            for a in teacher_uploaded_subject:
                print(a.subject.id)

            retrieve_my_students = Subscription.objects.filter(teacher__exact=current_teacher)
            print(retrieve_my_students)
            for students_retrieved in retrieve_my_students:
                my_student = students_retrieved.student

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            print(counter,'999000000000')

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body

            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'no_of_chats':no_of_chats,
                'retrieved_commented':retrieved_commented,
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

        no_of_chats = Chat.objects.filter(members= request.user.id)
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
        for my_studnts in list_of_students:
            print(my_studnts)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            print(counter,'999000000000')

            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body

            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'no_of_students':no_of_students,
                'no_of_chats':no_of_chats,
                'retrieved_commented':retrieved_commented,
            }
            return render(request,'transaction_details.html',context)


def FAQ(request):
	return render(request,'FAQ.html')

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

        no_of_chats = Chat.objects.filter(members= request.user.id)
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
        for my_studnts in list_of_students:
            print(my_studnts)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            print(counter,'999000000000')

            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()

            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body

            context={
                'subject_two':subject_two,
                'subject':subject,
                'subjects':subjects,
                'counter':counter,
                'retrieved_commented':retrieved_commented,
                'subject_one':subject_one,
                'no_of_chats':no_of_chats,
                'subject_id':subject_id,
                'subject_o':subject_o,
                'class_s':class_s,
                'no_of_students':no_of_students,
            }
            return render(request,'classes.html',context)

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

        no_of_chats = Chat.objects.filter(members= request.user.id)
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
        for my_studnts in list_of_students:
            print(my_studnts)

            retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
            counter = retrieve_my_comments.count()
            print(counter,'999000000000')

            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()
            retrieved_commented = retrieve_my_comments[:4]
            print(retrieved_commented)

            for notification in retrieved_commented:
                notifications = notification.body

            context={
                'subject_two':subject_two,
                'subject_one':subject_one,
                'counter':counter,
                'retrieved_commented':retrieved_commented,
                'subject_id':subject_id,
                'no_of_chats':no_of_chats,
                'subject_o':subject_o,
                'class_s':class_s,
                'no_of_students':no_of_students,
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
            email = EmailMessage(subject= f'Inquiry from {name} whose email is { email}',body=message,to=['capstoneprojects2020@gmail.com'],headers={'Message-ID': name,'Contact':phone_no })
            email.send()
            # send_mail(name, phone_no, email,message, ['capstoneprojects2020@gmail.com'])
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        # return redirect('success')
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

        comment_form = CommentForm(initial={'name': request.user,'email':request.user.userprofile.email})

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

        comment_form = CommentForm(initial={'name': request.user,'email':request.user.userprofile.email})

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

        no_of_chats = Chat.objects.filter(members= request.user.id)
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

            no_of_chats = Chat.objects.filter(members= request.user.id)
            no_of_chats = no_of_chats.count()
            chats = Chat.objects.filter(members__in=[request.user.id])
            print(chats)

            context={
                    'subject_two':subject_two,
                    'subject_one':subject_one,
                    'counter':counter,
                    'no_of_students':no_of_students,
                    'user_profile': request.user,
                    'no_of_chats':no_of_chats,
                    'chats': chats,
                }
            return render(request,'dialogue.html',context)
        else:
            for my_studnts in list_of_students:
                print(my_studnts)

                no_of_chats = Chat.objects.filter(members= request.user.id)
                no_of_chats = no_of_chats.count()
                chats = Chat.objects.filter(members__in=[request.user.id])

                retrieve_my_comments = Comment.objects.filter(name__exact=my_studnts,parent__exact = None)
                counter = retrieve_my_comments.count()
                print(counter,'999000000000')

                retrieved_commented = retrieve_my_comments[:4]
                print(retrieved_commented)

                for notification in retrieved_commented:
                    notifications = notification.body

                context={
                    'subject_two':subject_two,
                    'subject_one':subject_one,
                    'counter':counter,
                    'no_of_students':no_of_students,
                    'retrieved_commented':retrieved_commented,
                    'user_profile': request.user,
                    'no_of_chats':no_of_chats,
                    'chats': chats,
                    }
                return render(request, 'dialogue.html',context)



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
            no_of_chats = Chat.objects.filter(members= request.user.id)
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