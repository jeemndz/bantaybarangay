from django.db import models


class Evidence(models.Model):

    evidence_id = models.AutoField(primary_key=True)
    complaint_id = models.IntegerField()
    uploaded_by = models.IntegerField()
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=100, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    file_hash = models.CharField(max_length=64, null=True, blank=True)
    uploaded_at = models.DateTimeField()

    class Meta:
        db_table = "evidence"
        managed = False