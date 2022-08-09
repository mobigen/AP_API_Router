
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from .models import ApiInfo, ServerInfo, ApiParamInfo
from .forms import ApiInfoForm, ServerInfoForm, ApiParamInfoForm
# Create your views here.


def api_list(request):
    page = request.GET.get('page', 1)
    kw = request.GET.get('kw', "")

    api_list = ApiInfo.objects.order_by("-ctgry")
    if kw:
        api_list = api_list.filter(Q(api_nm__icontains=kw)).distinct()

    paginator = Paginator(api_list, 10)
    page_obj = paginator.get_page(page)

    context = {"api_list": page_obj, "page": page, "kw": kw}
    return render(request, "api/api_list.html", context)


def create_api(request):
    if request.method == "POST":
        category = get_object_or_404(
            ServerInfo, pk=request.POST.get("ctgry"))

        form = ApiInfoForm(request.POST)
        if form.is_valid():
            api = form.save(commit=False)
            api.ctgry = category
            api.save()
            return redirect("api:api_list")
        else:
            messages.error(request, form.errors.as_text())
    else:
        form = ApiInfoForm()
    context = {"form": form}
    return render(request, "api/create_api.html", context)


def update_api(request, api_nm):
    api = get_object_or_404(ApiInfo, pk=api_nm)
    param_list = ApiParamInfo.objects.filter(Q(api_nm=api_nm))
    if request.method == "POST":
        form = ApiInfoForm(request.POST, instance=api)
        if form.is_valid():
            form.save()
            return redirect("api:update_api", api_nm=api_nm)
        else:
            messages.error(request, form.errors.as_text())
    else:
        form = ApiInfoForm(instance=api)

    context = {"form": form, "api_nm": api_nm, "param_list": param_list}
    return render(request, "api/update_api.html", context)


def delete_api(request, api_nm):
    api = get_object_or_404(ApiInfo, pk=api_nm)

    api.delete()
    return redirect("api:api_list")


def create_param(request, api_nm):
    if request.method == "POST":
        form = ApiParamInfoForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, form.errors.as_text())
    return redirect("api:update_api", api_nm=api_nm)


def delete_param(request, api_nm, nm):
    param = ApiParamInfo.objects.filter(Q(api_nm=api_nm), Q(nm=nm))
    param.delete()
    return redirect("api:update_api", api_nm=api_nm)


def category_list(request):
    category_list = ServerInfo.objects.order_by("-nm")

    context = {"category_list": category_list}
    return render(request, "api/category_list.html", context)


def create_category(request):
    if request.method == "POST":
        form = ServerInfoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("api:category_list")
        else:
            messages.error(request, form.errors.as_text())
    else:
        form = ServerInfoForm()

    context = {"form": form}

    return render(request, "api/update_category.html", context)


def update_category(request, nm):
    category = get_object_or_404(ServerInfo, pk=nm)
    if request.method == "POST":
        form = ServerInfoForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("api:category_list")
        else:
            messages.error(request, form.errors.as_text())
    else:
        form = ServerInfoForm(instance=category)

    context = {"form": form, "nm": nm}
    return render(request, "api/update_category.html", context)


def delete_category(request, nm):
    category = get_object_or_404(ServerInfo, pk=nm)
    try:
        category.delete()
    except ProtectedError as err:
        messages.error(request, f"category - {nm}을 사용중인 API가 존재합니다.")
    return redirect("api:category_list")
