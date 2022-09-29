from django.db import models

# Create your models here.


class ServerInfo(models.Model):
    srvr_nm = models.CharField(max_length=64, primary_key=True)
    ip_adr = models.CharField(max_length=128)
    domn_nm = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        db_table = 'sitemng"."api_item_server_dtl'


class ApiInfo(models.Model):
    srvr_nm = models.ForeignKey(
        ServerInfo, on_delete=models.PROTECT, db_column="srvr_nm")
    api_nm = models.CharField(max_length=64, primary_key=True)
    route_url = models.CharField(max_length=256, unique=True)
    url = models.CharField(max_length=256, blank=True, null=True)
    mthd = models.CharField(max_length=64, blank=True, null=True)
    cmd = models.CharField(max_length=512, blank=True, null=True)
    mode = models.CharField(max_length=32)

    class Meta:
        db_table = 'sitemng"."api_item_bas'


class ApiParamInfo(models.Model):
    api_nm = models.ForeignKey(
        ApiInfo, on_delete=models.CASCADE, db_column="api_nm")
    nm = models.CharField(max_length=64)
    data_type = models.CharField(max_length=16)
    deflt_val = models.CharField(max_length=128)

    class Meta:
        db_table = 'sitemng"."api_item_param_dtl'
        unique_together = (('api_nm', 'nm'),)
