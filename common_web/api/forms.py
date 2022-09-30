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
        fields = ("srvr_nm", "ip_adr")  # , "domn_nm")
        labels = {"srvr_nm": "서버명", "ip_adr": "IP 주소"}  # , "domn_nm": "도메인명"}
        widgets = {"srvr_nm": forms.TextInput()}


class ApiInfoForm(forms.Form):
    api_nm = forms.CharField(label="API명", max_length=64)
    route_url = forms.CharField(
        label="라우트 URL", max_length=256, required=False)
    url = forms.CharField(label="URL", max_length=256, required=False)
    cmd = forms.CharField(label="명령어", max_length=512, required=False)
    mode = forms.ChoiceField(
        label="모드", choices=MODE)
    srvr_nm = forms.ChoiceField(label="서버명", choices=[(
        category.srvr_nm, category.srvr_nm) for category in ServerInfo.objects.all()])
    mthd = forms.ChoiceField(label="메소드", choices=METHOD)


class ApiParamInfoForm(forms.ModelForm):
    class Meta:
        model = ApiParamInfo
        fields = ("api_nm", "nm", "data_type", "deflt_val")
        labels = {"api_nm": "API명", "nm": "명",
                  "data_type": "데이터 유형", "deflt_val": "초기설정 값"}
