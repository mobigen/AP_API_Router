from django.urls import path
from . import views

app_name = 'table'

urlpatterns = [
    path('', views.table_list, name='table_list'),
    path('<str:table_id>', views.table_detail, name='table_detail'),
    path('<str:table_id>/column/<str:eng_nm>',
         views.delete_column, name='delete_column'),
    path('<str:table_id>/delete',
         views.delete_table, name='delete_table'),
]
