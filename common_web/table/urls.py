from django.urls import path
from . import views

app_name = 'table'

urlpatterns = [
    path('', views.table_list, name='table_list'),
    path('<str:tbl_id>', views.table_detail, name='table_detail'),
    path('<str:tbl_id>/csv', views.save_csv, name="save_csv"),

    path('create/', views.create_table, name='create_table'),
    path('<str:tbl_id>/update', views.update_table, name='update_table'),
    path('<str:tbl_id>/column/delete/<str:eng_nm>',
         views.delete_column, name='delete_column'),
    path('<str:tbl_id>/column/update/<str:eng_nm>',
         views.update_column, name='update_column'),
    path('<str:tbl_id>/delete',
         views.delete_table, name='delete_table'),

]
