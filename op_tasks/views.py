from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.conf import settings

import datetime
from op_tasks.models import Dataset, Product, OpTask, UserProfile, TaskListItem
from op_tasks.forms import UserForm

# @login_required
# def index(request):
# 	op_task = OpTask.objects.get(pk=1)	
# 	return render(request, 'question.html', {'op_task': op_task})

def set_cookie(response, key, value, days_expire = 7):
  if days_expire is None:
    max_age = 365 * 24 * 60 * 60  #one year
  else:
    max_age = days_expire * 24 * 60 * 60 
  expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
  response.set_cookie(key, value, 
  	max_age=max_age, 
  	expires=expires, 
  	domain=settings.SESSION_COOKIE_DOMAIN, 
  	secure=None)
   
def product(request, task_pk):
    if request.method == 'POST':
        user = request.user
        userprofile = user.userprofile

        print 'Task primary key: ', task_pk, ' completed'
        try:
            # get current sequence from user, this ensures that current user
            # can only get sequences assigned to him/her
            current_tasklistitem = userprofile.tasklistitem_set.get(pk=task_pk)
        except:
            return HttpResponseRedirect("/op_tasks/task_list")

        tasklist_length = len(userprofile.tasklistitem_set.all())
        
        # if it's not the last task, make the next task active
        if current_tasklistitem.index < (tasklist_length - 1):
            next_tasklistitem = userprofile.tasklistitem_set.get(index=current_tasklistitem.index+1)
        
        # if you got here because you just completed a task,
        # then set it complete and make the exit task active
        if current_tasklistitem.task_complete == False:
            current_tasklistitem.task_complete = True
            current_tasklistitem.task_active = False
            current_tasklistitem.exit_active = True
        
        # you likely got here because you just completed an exit task
        # so mark it complete and move 
        else:
            current_tasklistitem.exit_active = False
            current_tasklistitem.exit_complete = True
            print 'survey complete', current_tasklistitem.index
            if current_tasklistitem.index < 1:
                next_tasklistitem.task_active = True
                next_tasklistitem.save()
            else:
                current_tasklistitem.save()
        current_tasklistitem.save()
        return HttpResponseRedirect("/op_tasks/task_list")

    # if method is GET just show the product page
    user = request.user
    userprofile = user.userprofile
    tasklistitem = TaskListItem.objects.get(pk=task_pk)
    current_task = tasklistitem.op_task
    request.session['current_optask'] = current_task.pk

    response = render(request, 'product.html', {
    	'product': tasklistitem.product,
        'task_pk': task_pk,
        'product_url': tasklistitem.product.url + ('?USID=%s::%s' % (userprofile.user_hash, tasklistitem.pk)),
    	'op_task': current_task
    	})
    set_cookie(response, 'USID', '%s::%s' % (userprofile.user_hash, tasklistitem.pk))
    return response

def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        print "POST"
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        # profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid(): # and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.username = user.email
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            userprofile = UserProfile()
            userprofile.user = user

            # Now we save the UserProfile model instance.
            userprofile.save()

            # Finally we assign tasks to the new user
            # Get a random product, get a random order of tasks
            # And save them to the task list
            product = Product.objects.filter(is_active=True).order_by('?')[0]
            dataset = product.dataset
            tasks = dataset.optask_set.filter(is_active=True).order_by('?')

            for index, task in enumerate(tasks):
                if index==0:
                    active=True
                else:
                    active=False
                TaskListItem(userprofile=userprofile, op_task=task, product=product, 
                    index=index, task_active=active).save()


            # Update our variable to tell the template registration was successful.
            registered = True
            print "successful registration"
            return HttpResponseRedirect("/op_tasks/task_list/")

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors#, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        #profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render_to_response(
            'registration/register.html',
            {'user_form': user_form, 'registered': registered},
            context)

def logout_participant(request):
    """
    Log users out and re-direct them to the main page.
    """
    logout(request)
    return HttpResponseRedirect('/')

def login_participant(request):
	# Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/op_tasks/task_list')
                # return render(request, 'task_list.html', {'user': request.user})
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your XDATA account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('registration/login.html', {}, context)

	# return login_view(request, authentication_form=MyAuthForm)

@login_required(login_url='/op_tasks/login')
def task_list(request):
    # print [x.both_complete for x in userprofile.tasklistitem_set.all()]
    user = request.user
    userprofile = user.userprofile
    all_complete = all([x.both_complete for x in userprofile.tasklistitem_set.all()])
    return render(request, 'task_list.html', 
        {'userprofile': userprofile, 'all_complete': all_complete}
        )

def intro(request, process=None):
    if process == 'register':
        follow = '/op_tasks/register'
    elif process == 'login':
        follow = '/op_tasks/login'
    return render(request, 'intro.html', {'user': request.user, 'follow': follow})

def login_intro(request):
    return render(request, 'login_intro.html', {'user': request.user})

def instruct(request, read=None):
    user = request.user
    userprofile = user.userprofile

    if read == 'experiment':
        userprofile.exp_inst_complete = True

    elif read == 'portal':
        userprofile.portal_inst_complete = True

    elif read == 'product':
        user.userprofile.task_inst_complete = True

    userprofile.save()
    product = request.user.userprofile.tasklistitem_set.all()[0].product
    return render(request, 'instruction_home.html', {'user': request.user, 'product': product})

def exp_instruct(request):
    return render(request, 'instructions/exp_instructions.html', {'user': request.user})

def portal_instruct(request):
    return render(request, 'instructions/portal_instructions.html', {'user': request.user})

def product_instruct(request):
    return render(request, 'instructions/product_instructions.html', {'user': request.user})