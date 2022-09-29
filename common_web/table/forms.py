
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
    db_schema = forms.ChoiceField(
        label="카테고리명", choices=CATEGORY)

    class Meta:
        model = TableInfo
        fields = ("tbl_nm", "tbl_kor_nm", "db_schema")
        labels = {"tbl_nm": "테이블명", "tbl_kor_nm": "테이블 한글명"}


class ColumnInfoForm(forms.ModelForm):

    class Meta:
        model = ColumnInfo
        fields = ("eng_nm", "kor_nm", "data_type")
        labels = {
            "eng_nm": "영문명",
            "kor_nm": "한글명",
            "data_type": "데이터 유형"
        }
