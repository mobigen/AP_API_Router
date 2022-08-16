from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
import uuid
from .models import TableInfo, ColumnInfo
from .forms import TableInfoForm, ColumnInfoForm
from commonUtil.Utils import connect_db

# Create your views here.

db_info = {
    "host": "192.168.100.126",
    "port": 25432,
    "user": "dpmanager",
    "password": "hello.dp12#$",
    "database": "dataportal",
    "schema": "users,meta,sitemng,board,analysis,sysconfig"
}
'''
db_info = {
    "host": "192.168.101.43",
    "port": 5432,
    "user": "dhub",
    "password": "dhub.12#",
    "database": "dhub",
    "schema": "meta,api,sitemng"
}
'''


def table_list(request):
    table_list = TableInfo.objects.order_by("-table_nm")

    if request.method == "POST":
        form = TableInfoForm(request.POST)
        if form.is_valid():
            try:
                db = connect_db(db_info)

                table_nm = request.POST.get("table_nm")
                schema = request.POST.get("schema")
                db.execute(
                    f'CREATE TABLE {schema}.{table_nm} ( idx serial4 not null );')
            except Exception as err:
                messages.error(request, err)
            else:
                table = form.save(commit=False)
                table.table_id = uuid.uuid4()
                table.save()
            return redirect("table:table_list")
        else:
            messages.error(request, form.errors)
    else:
        form = TableInfoForm()
    context = {"table_list": table_list, "form": form}
    return render(request, "table/table_list.html", context)


def table_detail(request, table_id):
    table = get_object_or_404(TableInfo, pk=table_id)
    column_list = ColumnInfo.objects.filter(Q(table_id=table_id))

    if request.method == "POST":
        form = ColumnInfoForm(request.POST)
        if form.is_valid():
            try:
                db = connect_db(db_info)

                table_nm = table.table_nm
                eng_nm = request.POST.get("eng_nm")
                data_type = request.POST.get("data_type")
                db.execute(f'ALTER TABLE {table_nm} ADD {eng_nm} {data_type};')
            except Exception as err:
                messages.error(request, err)
            else:
                column = form.save(commit=False)
                column.table = table
                column.save()
            return redirect("table:table_detail", table_id=table_id)
        else:
            messages.error(request, form.errors)
    else:
        form = ColumnInfoForm()

    context = {"table": table, "column_list": column_list, "form": form}
    return render(request, "table/table_detail.html", context)


def delete_table(request, table_id):
    table = get_object_or_404(TableInfo, pk=table_id)

    try:
        db = connect_db(db_info)
        db.execute(f'DROP TABLE {table.table_nm};')
    except Exception as err:
        messages.error(request, err)
    else:
        table.delete()
    return redirect("table:table_list")


def delete_column(request, table_id, eng_nm):
    table = get_object_or_404(TableInfo, pk=table_id)
    column = ColumnInfo.objects.filter(
        Q(table_id=table_id), Q(eng_nm=eng_nm))

    try:
        db = connect_db(db_info)
        db.execute(f'ALTER TABLE {table.table_nm} DROP {eng_nm};')
    except Exception as err:
        messages.error(request, err)
    else:
        column.delete()
    return redirect("table:table_detail", table_id=table_id)
