from django.conf.urls import patterns, url
from django.conf import settings
from django.contrib.staticfiles import views as vs
from exp_portal import views

urlpatterns= patterns('',
	url(r'^$', views.home_page, name='home'),
	url(r'^status$', views.view_status, name='view_status'),
	url(r'^products$', views.view_products, name='view_products'),
	url(r'^submit$', views.submit_task, name='submit_task'),
	url(r'^newTask$', views.new_task, name='new_task'),
	url(r'^taskAdded$', views.task_added, name='task_added'),
	url(r'^users$', views.view_users, name='view_users'), 
	url(r'^tasks$', views.view_tasks, name='view_tasks'),
	url(r'^tasks/completed$', views.view_completed, name='view_completed'), 
	url(r'^tasks/incomplete$', views.view_incomplete, name='view_incomplete'),
	url(r'^manage$', views.manage_tasks, name='manage_tasks'),
	)