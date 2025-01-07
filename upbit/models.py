from django.db import models

# Create your models here.
class Market(models.Model):
    
    log_dt = models.DateTimeField(primary_key = True)
    market = models.CharField(max_length = 45)
    price = models.FloatField()
    volume = models.FloatField()
    amount = models.FloatField()
    
    class Meta:
        managed = False
        db_table = 'tb_market'
        unique_together = (('log_dt','market'),)