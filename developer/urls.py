from django.conf.urls import patterns, url
from django.conf import settings
from django.contrib.staticfiles import views as vs
from developer import views

urlpatterns= patterns('',
	url(r'^$', views.home_page, name='home'),
	url(r'^status$', views.view_status, name='view_status'),
	url(r'^products$', views.view_products, name='view_products'),
	url(r'^submit$', views.submit_product, name='submit_product'),
	url(r'^newProduct$', views.newProduct, name='newProduct'),
    url(r'^product_comp$', views.product_comp, name='product_comp'),
	)