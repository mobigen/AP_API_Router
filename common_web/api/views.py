
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from .models import ApiInfo, ServerInfo, ApiParamInfo
from .forms import ApiInfoForm, ServerInfoForm, ApiParamInfoForm
import requests
# Create your views here.

RELOAD_URL = "http://192.168.100.126:8010/api/reload"


def api_list(request):
    page = request.GET.get('page', 1)
    kw = request.GET.get('kw', "")

    api_list = ApiInfo.objects.order_by("-srvr_nm")
    if kw:
        api_list = api_list.filter(Q(api_nm__icontains=kw)).distinct()

    paginator = Paginator(api_list, 10)
    page_obj = paginator.get_page(page)

    context = {"api_list": page_obj, "page": page, "kw": kw}
    return render(request, "api/api_list.html", context)


def create_api(request):
    if request.method == "POST":
        category = get_object_or_404(
            ServerInfo, pk=request.POST.get("srvr_nm"))
        form = ApiInfoForm(request.POST)
        if form.is_valid():
            api = ApiInfo(srvr_nm=category,
                          api_nm=form.cleaned_data["api_nm"],
                          route_url=form.cleaned_data["route_url"],
                          url=form.cleaned_data["url"],
                          mthd=form.cleaned_data["mthd"],
                          cmd=form.cleaned_data["cmd"],
                          mode=form.cleaned_data["mode"])
            api.save()
            requests.get(RELOAD_URL)
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
        category = get_object_or_404(
            ServerInfo, pk=request.POST.get("srvr_nm"))
        form = ApiInfoForm(request.POST)
        if form.is_valid():
            api.srvr_nm = category
            api.api_nm = request.POST.get("api_nm")
            api.route_url = request.POST.get("route_url")
            api.url = request.POST.get("url")
            api.mthd = request.POST.get("mthd")
            api.cmd = request.POST.get("cmd")
            api.mode = request.POST.get("mode")
            api.save()
            requests.get(RELOAD_URL)
            return redirect("api:api_list")
        else:
            messages.error(request, form.errors.as_text())
    else:
        form_data = api.__dict__
        form_data["srvr_nm"] = form_data["srvr_nm_id"]
        form = ApiInfoForm(form_data)

    context = {"form": form, "api_nm": api_nm, "param_list": param_list}
    return render(request, "api/update_api.html", context)


def delete_api(request, api_nm):
    api = get_object_or_404(ApiInfo, pk=api_nm)

    api.delete()
    requests.get(RELOAD_URL)

    return redirect("api:api_list")


def create_param(request, api_nm):
    if request.method == "POST":
        form = ApiParamInfoForm(request.POST)
        if form.is_valid():
            form.save()
            requests.get(RELOAD_URL)
        else:
            messages.error(request, form.errors.as_text())
    return redirect("api:update_api", api_nm=api_nm)


def delete_param(request, api_nm, nm):
    param = ApiParamInfo.objects.filter(Q(api_nm=api_nm), Q(nm=nm))
    param.delete()
    print("AAA")
    requests.get(RELOAD_URL)
    print("BBB")

    return redirect("api:update_api", api_nm=api_nm)


def category_list(request):
    category_list = ServerInfo.objects.order_by("-srvr_nm")

    context = {"category_list": category_list}
    return render(request, "api/category_list.html", context)


def create_category(request):
    if request.method == "POST":
        form = ServerInfoForm(request.POST)
        if form.is_valid():
            form.save()
            requests.get(RELOAD_URL)
            return redirect("api:category_list")
        else:
            messages.error(request, form.errors.as_text())
    else:
        form = ServerInfoForm()

    context = {"form": form}

    return render(request, "api/update_category.html", context)


def update_category(request, srvr_nm):
    category = get_object_or_404(ServerInfo, pk=srvr_nm)
    if request.method == "POST":
        form = ServerInfoForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            requests.get(RELOAD_URL)
            return redirect("api:category_list")
        else:
            messages.error(request, form.errors.as_text())
    else:
        form = ServerInfoForm(instance=category)

    context = {"form": form, "nm": srvr_nm}
    return render(request, "api/update_category.html", context)


def delete_category(request, srvr_nm):
    category = get_object_or_404(ServerInfo, pk=srvr_nm)
    try:
        category.delete()
        requests.get(RELOAD_URL)
    except ProtectedError as err:
        messages.error(request, f"category - {srvr_nm}을 사용중인 API가 존재합니다.")
    return redirect("api:category_list")
