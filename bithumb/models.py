from django.db import models

# Create your models here.
class MarketInfo(models.Model):
    
    
    market = models.CharField(primary_key = True, max_length = 45)
    capitalization = models.FloatField()
    
    class Meta:
        managed = False
        db_table = 'tb_market_info'
        unique_together = (('market'))

class Market(models.Model):
    
    log_dt = models.DateTimeField(primary_key = True)
    market = models.CharField(max_length = 45)
    price = models.FloatField()
    
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

class MarketDay(models.Model):
    
    date = models.DateField(primary_key = True)
    market = models.CharField(max_length = 45)
    opening_price = models.FloatField()
    trade_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    volume = models.FloatField()
    amount = models.FloatField()
    
    class Meta:
        managed = False
        db_table = 'tb_market_day'
        unique_together = (('date','market'),)

class MA60Minutes(models.Model):
    
    log_dt = models.DateTimeField(primary_key = True)
    market = models.CharField(max_length = 45)
    ma_10 = models.FloatField()
    ma_20 = models.FloatField()
    ma_34 = models.FloatField()
    ma_50 = models.FloatField()
    ma_100 = models.FloatField()
    ma_200 = models.FloatField()
    ma_400 = models.FloatField()
    ma_800 = models.FloatField()
    golden_cross_10_34 = models.IntegerField()
    dead_cross_10_34 = models.IntegerField()
    created_at = models.TimeField()
    
    
    class Meta:
        managed = False
        db_table = 'tb_ma_60_minutes'
        unique_together = (('log_dt','market'),)

class MADays(models.Model):
    
    date = models.DateField(primary_key = True)
    market = models.CharField(max_length = 45)
    ma_10 = models.FloatField()
    ma_20 = models.FloatField()
    ma_34 = models.FloatField()
    ma_50 = models.FloatField()
    ma_100 = models.FloatField()
    ma_200 = models.FloatField()
    ma_400 = models.FloatField()
    ma_800 = models.FloatField()
    golden_cross_10_34 = models.IntegerField()
    dead_cross_10_34 = models.IntegerField()
    created_at = models.TimeField()
    
    
    class Meta:
        managed = False
        db_table = 'tb_ma_days'
        unique_together = (('date','market'),)
        