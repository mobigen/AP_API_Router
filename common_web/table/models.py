from django.db import models

# Create your models here.


class TableInfo(models.Model):
    table_id = models.CharField(max_length=128, primary_key=True)
    schema = models.CharField(max_length=64)
    table_nm = models.CharField(max_length=128)

    class Meta:
        db_table = 'meta"."tb_table_list'
        unique_together = (('schema', 'table_nm'),)


class ColumnInfo(models.Model):
    table = models.ForeignKey(TableInfo, on_delete=models.CASCADE)
    kor_nm = models.CharField(max_length=128)
    eng_nm = models.CharField(max_length=128)
    data_type = models.CharField(max_length=32)

    class Meta:
        db_table = 'meta"."tb_table_column_info'
