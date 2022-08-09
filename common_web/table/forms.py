
from django import forms
from .models import TableInfo, ColumnInfo

CATEGORY = (
    ("analysis", "analysis"),
    ("board", "board"),
    ("iag", "iag"),
    ("meta", "meta"),
    ("sitemng", "sitemng"),
    ("sysconfig", "sysconfig"),
    ("users", "users"),
)


class TableInfoForm(forms.ModelForm):
    schema = forms.ChoiceField(
        label="카테고리명", choices=CATEGORY)

    class Meta:
        model = TableInfo
        fields = ("table_nm", "schema")
        labels = {"table_nm": "테이블명"}


class ColumnInfoForm(forms.ModelForm):

    class Meta:
        model = ColumnInfo
        fields = ("eng_nm", "kor_nm", "data_type")
        labels = {
            "eng_nm": "컬럼명(영어)",
            "kor_nm": "컬럼명(한글)",
            "data_type": "데이터 타입"
        }
