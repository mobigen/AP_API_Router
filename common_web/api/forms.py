from django import forms
from .models import ServerInfo, ApiInfo, ApiParamInfo

MODE = (
    ("MESSAGE PASSING", "MESSAGE PASSING"),
    ("REMOTE CALL", "REMOTE CALL"),
)
METHOD = (
    ("GET", "GET"),
    ("POST", "POST"),
)

CATEGORY = (
    ("TEST", "TEST")
)


class ServerInfoForm(forms.ModelForm):
    class Meta:
        model = ServerInfo
        fields = ("nm", "ip_adr")  # , "domn_nm")
        labels = {"nm": "카테고리명", "ip_adr": "IP"}  # , "domn_nm": "도메인명"}
        widgets = {"nm": forms.TextInput()}


class ApiInfoForm(forms.ModelForm):
    mode = forms.ChoiceField(
        label="동작방식", choices=MODE)
    ctgry = forms.ChoiceField(label="카테고리명", choices=[(
        category.nm, category.nm) for category in ServerInfo.objects.all()])
    meth = forms.ChoiceField(label="Method", choices=METHOD)

    class Meta:
        model = ApiInfo
        fields = ("api_nm", "route_url", "url", "cmd", "mode", "meth")
        labels = {"api_nm": "API명", "route_url": "Route URL",
                  "url": "Service URL", "cmd": "Remote CMD"}


class ApiParamInfoForm(forms.ModelForm):
    class Meta:
        model = ApiParamInfo
        fields = ("api_nm", "nm", "data_type", "deflt_val")
        labels = {"api_nm": "API명", "nm": "파라미터명",
                  "data_type": "데이터타입", "deflt_val": "디폴트값"}
