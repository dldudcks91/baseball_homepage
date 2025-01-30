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

class MarketHour(models.Model):
    
    log_dt = models.DateTimeField(primary_key = True)
    market = models.CharField(max_length = 45)
    opening_price = models.FloatField()
    trade_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    volume = models.FloatField()
    amount = models.FloatField()
    
    class Meta:
        managed = False
        db_table = 'tb_market_hour'
        unique_together = (('log_dt','market'),)

class MarketInfo(models.Model):
    
    
    market = models.CharField(max_length = 45, primary_key = True)
    symbol = models.CharField(max_length = 45)
    korean_name = models.CharField(max_length = 45)
    english_name = models.CharField(max_length = 45)
    
    gecko_id = models.CharField(max_length = 45)
    issue_month = models.CharField(max_length = 7)
    listing_month = models.CharField(max_length = 7)
    capitalization = models.FloatField()
    class Meta:
        managed = False
        db_table = 'tb_market_info'


class MarketSupply(models.Model):
    
    
    
    symbol = models.CharField(max_length = 45, primary_key = True)
    capitalization = models.BigIntegerField()  
    max_supply = models.BigIntegerField()
    now_supply = models.BigIntegerField()  
    
    
    class Meta:
        managed = False
        db_table = 'tb_market_supply'
        