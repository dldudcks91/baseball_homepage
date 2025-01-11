from django.db import models

# Create your models here.
class Market(models.Model):
    
    log_dt = models.DateTimeField(primary_key = True)
    market = models.CharField(max_length = 45)
    price = models.FloatField()
    volume = models.FloatField()
    amount = models.FloatField()
    price_foreign = models.FloatField()
    class Meta:
        managed = False
        db_table = 'tb_market'
        unique_together = (('log_dt','market'),)

class MarketInfo(models.Model):
    
    
    market = models.CharField(max_length = 45, primary_key = True)
    symbol = models.CharField(max_length = 45)
    korean_name = models.CharField(max_length = 45)
    english_name = models.CharField(max_length = 45)
    capitalization = models.FloatField()
    gecko_id = models.CharField(max_length = 45)
    
    
    class Meta:
        managed = False
        db_table = 'tb_market_info'
        