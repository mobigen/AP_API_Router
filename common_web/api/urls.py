from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('', views.api_list, name='api_list'),
    path('create/', views.create_api, name='create_api'),
    path('update/<str:api_nm>', views.update_api, name='update_api'),
    path('delete/<str:api_nm>', views.delete_api, name='delete_api'),

    path("<str:api_nm>/create/param", views.create_param, name="create_param"),
    path("<str:api_nm>/delete/param/<str:nm>",
         views.delete_param, name="delete_param"),

    path('category/', views.category_list, name='category_list'),
    path('category/create', views.create_category, name='create_category'),
    path('category/update/<str:srvr_nm>',
         views.update_category, name='update_category'),
    path('category/delete/<str:srvr_nm>',
         views.delete_category, name='delete_category'),
]
