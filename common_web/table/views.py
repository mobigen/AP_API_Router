from base64 import encode
import csv
from email import header
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
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
    "database": "ktportal",
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
    page = request.GET.get('page', 1)
    kw = request.GET.get('kw', "")
    table_list = TableInfo.objects.order_by("-db_schema")
    if kw:
        table_list = table_list.filter(Q(tbl_nm__icontains=kw)).distinct()

    paginator = Paginator(table_list, 10)
    page_obj = paginator.get_page(page)

    if request.method == "POST":
        form = TableInfoForm(request.POST)
        if form.is_valid():
            try:
                db = connect_db(db_info)

                tbl_nm = request.POST.get("tbl_nm")
                db_schema = request.POST.get("db_schema")
                db.execute(
                    f'CREATE TABLE {db_schema}.{tbl_nm} ();')
            except Exception as err:
                messages.error(request, err)
            else:
                table = form.save(commit=False)
                table.tbl_id = uuid.uuid4()
                table.save()
            return redirect("table:table_list")
        else:
            messages.error(request, form.errors)
    else:
        form = TableInfoForm()
    context = {"table_list": page_obj, "form": form, "page": page, "kw": kw}
    return render(request, "table/table_list.html", context)


def create_table(request):
    if request.method == "POST":
        form = TableInfoForm(request.POST)
        if form.is_valid():
            try:
                db = connect_db(db_info)

                tbl_nm = request.POST.get("tbl_nm")
                db_schema = request.POST.get("db_schema")
                db.execute(
                    f'CREATE TABLE {db_schema}.{tbl_nm} ();')
            except Exception as err:
                messages.error(request, err)
            else:
                table = form.save(commit=False)
                table.tbl_id = uuid.uuid4()
                table.save()
            return redirect("table:table_list")
        else:
            messages.error(request, form.errors)
    else:
        form = TableInfoForm()
    context = {"form": form}
    return render(request, "table/create_table.html", context)


def update_table(request, tbl_id):
    table = get_object_or_404(TableInfo, pk=tbl_id)
    old_nm = table.tbl_nm

    if request.method == "POST":
        form = TableInfoForm(request.POST, instance=table)
        if form.is_valid():
            try:
                db = connect_db(db_info)
                new_nm = request.POST.get("tbl_nm")
                if old_nm != new_nm:
                    db.execute(f'ALTER TABLE {old_nm} RENAME TO {new_nm};')
            except Exception as err:
                messages.error(request, err)
            else:
                form.save()
            return redirect("table:table_list")
        else:
            messages.error(request, form.errors.as_text())
    else:
        form = TableInfoForm(instance=table)
    context = {"form": form}
    return render(request, "table/update_table.html", context)


def table_detail(request, tbl_id):
    table = get_object_or_404(TableInfo, pk=tbl_id)
    column_list = ColumnInfo.objects.filter(Q(tbl_id=tbl_id))

    if request.method == "POST":
        form = ColumnInfoForm(request.POST)
        if form.is_valid():
            try:
                db = connect_db(db_info)

                tbl_nm = table.tbl_nm
                eng_nm = request.POST.get("eng_nm")
                data_type = request.POST.get("data_type")
                db.execute(f'ALTER TABLE {tbl_nm} ADD {eng_nm} {data_type};')
            except Exception as err:
                messages.error(request, err)
            else:
                column = form.save(commit=False)
                column.tbl_id = table
                column.save()
            return redirect("table:table_detail", tbl_id=tbl_id)
        else:
            messages.error(request, form.errors)
    else:
        form = ColumnInfoForm()

    context = {"table": table, "column_list": column_list, "form": form}
    return render(request, "table/table_detail.html", context)


def delete_table(request, tbl_id):
    table = get_object_or_404(TableInfo, pk=tbl_id)

    try:
        db = connect_db(db_info)
        db.execute(f'DROP TABLE {table.tbl_nm};')
    except Exception as err:
        messages.error(request, err)
    else:
        table.delete()
    return redirect("table:table_list")


def update_column(request, tbl_id, eng_nm):
    table = get_object_or_404(TableInfo, pk=tbl_id)
    column = ColumnInfo.objects.filter(
        Q(tbl_id=tbl_id), Q(eng_nm=eng_nm))[0]

    if request.method == "POST":
        form = ColumnInfoForm(request.POST, instance=column)
        if form.is_valid():
            try:
                db = connect_db(db_info)
                table_nm = table.tbl_nm
                new_nm = request.POST.get("eng_nm")
                if eng_nm != new_nm:
                    db.execute(
                        f'ALTER TABLE {table_nm} RENAME COLUMN {eng_nm} TO {new_nm};')
            except Exception as err:
                messages.error(request, err)
            else:
                form.save()
            return redirect("table:table_detail", tbl_id=tbl_id)
        else:
            messages.error(request, form.errors.as_text())
    else:
        form = ColumnInfoForm(instance=column)
    context = {"form": form, "tbl_id": tbl_id}
    return render(request, "table/update_column.html", context)


def delete_column(request, tbl_id, eng_nm):
    table = get_object_or_404(TableInfo, pk=tbl_id)
    column = ColumnInfo.objects.filter(
        Q(tbl_id=tbl_id), Q(eng_nm=eng_nm))

    try:
        db = connect_db(db_info)
        db.execute(f'ALTER TABLE {table.tbl_nm} DROP {eng_nm};')
    except Exception as err:
        messages.error(request, err)
    else:
        column.delete()
    return redirect("table:table_detail", tbl_id=tbl_id)


def save_csv(request, tbl_id):
    table = get_object_or_404(TableInfo, pk=tbl_id)
    column_list = ColumnInfo.objects.filter(Q(tbl_id=tbl_id))
    response = HttpResponse(content_type='text/csv', headers={
                            'Content-Disposition': f'attachment; filename="{table.tbl_nm}.csv"'})
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    writer.writerow(['컬럼명(영어)', '컬럼명(한글)', '데이터 타입'])
    for column in column_list:
        writer.writerow([column.eng_nm, column.kor_nm, column.data_type])
    return response
