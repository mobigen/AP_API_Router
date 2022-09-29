from django.db import models

# Create your models here.


class TableInfo(models.Model):
    tbl_id = models.CharField(max_length=128, primary_key=True)
    db_schema = models.CharField(max_length=64)
    tbl_nm = models.CharField(max_length=128)
    tbl_kor_nm = models.CharField(max_length=128)

    class Meta:
        db_table = 'meta"."tbl_item_bas'
        unique_together = (('db_schema', 'tbl_nm'),)


class ColumnInfo(models.Model):
    tbl_id = models.ForeignKey(
        TableInfo, on_delete=models.CASCADE, db_column="tbl_id")
    kor_nm = models.CharField(max_length=128)
    eng_nm = models.CharField(max_length=128)
    data_type = models.CharField(max_length=32)

    class Meta:
        db_table = 'meta"."tbl_item_coln_dtl'
