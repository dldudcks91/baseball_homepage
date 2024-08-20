# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User

class AuthGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)





class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'

class TeamInfo(models.Model):
    year = models.IntegerField(primary_key=True)
    team_num = models.IntegerField()
    team_name = models.CharField(max_length=3, blank=True, null=True)
    stadium = models.CharField(max_length=2, blank=True, null=True)
    total_game_num = models.IntegerField(blank=True, null=True)
    win = models.IntegerField(blank=True, null=True)
    lose = models.IntegerField(blank=True, null=True)
    draw = models.IntegerField(blank=True, null=True)
    win_rate = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team_info'
        unique_together = (('year', 'team_num'),)
        ordering = ['-win_rate','-win']
        
class GameInfo(models.Model):
    game_idx = models.CharField(primary_key=True, max_length=14)
    home_name = models.CharField(max_length=3, blank=True, null=True)
    away_name = models.CharField(max_length=3, blank=True, null=True)
    stadium = models.CharField(max_length=2, blank=True, null=True)
    end = models.CharField(max_length=4, blank=True, null=True)
    etc = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'game_info'
        
class TeamGameInfo(models.Model):
    #game_idx = models.CharField(max_length=14)
    game_idx = models.ForeignKey(GameInfo, models.CASCADE, db_column='game_idx', blank=True, null=True)
    team_game_idx = models.CharField( max_length=9, primary_key = True)
    #year = models.ForeignKey('TeamInfo', models.DO_NOTHING, db_column='year', blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    
    #team_num = models.ForeignKey('TeamInfo', models.DO_NOTHING, db_column='team_num', blank=True, null=True,related_name='teamgameinfo_team_num_set')
    team_num = models.IntegerField(blank=True, null=True)
    foe_num = models.IntegerField(blank=True, null=True)
    game_num = models.IntegerField(blank=True, null=True)
    home_away = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'team_game_info'
        ordering = ['game_idx','home_away']
        
class BatterRecord(models.Model):
    team_game_idx = models.OneToOneField('TeamGameInfo', models.DO_NOTHING, db_column='team_game_idx', primary_key=True)
    bo = models.IntegerField()
    po = models.IntegerField()
    name = models.CharField(max_length=5, blank=True, null=True)
    b1 = models.IntegerField(blank=True, null=True)
    b2 = models.IntegerField(blank=True, null=True)
    b3 = models.IntegerField(blank=True, null=True)
    hr = models.IntegerField(blank=True, null=True)
    bb = models.IntegerField(blank=True, null=True)
    hbp = models.IntegerField(blank=True, null=True)
    ibb = models.IntegerField(blank=True, null=True)
    sac = models.IntegerField(blank=True, null=True)
    sf = models.IntegerField(blank=True, null=True)
    so = models.IntegerField(blank=True, null=True)
    go = models.IntegerField(blank=True, null=True)
    fo = models.IntegerField(blank=True, null=True)
    gidp = models.IntegerField(blank=True, null=True)
    etc = models.IntegerField(blank=True, null=True)
    h = models.IntegerField(blank=True, null=True)
    tbb = models.IntegerField(blank=True, null=True)
    ab = models.IntegerField(blank=True, null=True)
    pa = models.IntegerField(blank=True, null=True)
    xr = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'batter_record'
        unique_together = (('team_game_idx', 'bo', 'po'),)
class PitcherRecord(models.Model):
    
    team_game_idx = models.OneToOneField('TeamGameInfo', models.DO_NOTHING, db_column='team_game_idx', primary_key=True)
    name = models.CharField(max_length=5)
    po = models.IntegerField()
    inn = models.FloatField(blank=True, null=True)
    tbf = models.IntegerField(blank=True, null=True)
    np = models.IntegerField(blank=True, null=True)
    ab = models.IntegerField(blank=True, null=True)
    h = models.IntegerField(blank=True, null=True)
    hr = models.IntegerField(blank=True, null=True)
    tbb = models.IntegerField(blank=True, null=True)
    so = models.IntegerField(blank=True, null=True)
    r = models.IntegerField(blank=True, null=True)
    er = models.IntegerField(blank=True, null=True)
    fip = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pitcher_record'
        unique_together = (('team_game_idx', 'po'))
        


class ScoreRecord(models.Model):
    team_game_idx = models.OneToOneField('TeamGameInfo', models.DO_NOTHING, db_column='team_game_idx', primary_key=True)
    result = models.CharField(max_length=4, blank=True, null=True)
    x1 = models.CharField(max_length=2, blank=True, null=True)
    x2 = models.CharField(max_length=2, blank=True, null=True)
    x3 = models.CharField(max_length=2, blank=True, null=True)
    x4 = models.CharField(max_length=2, blank=True, null=True)
    x5 = models.CharField(max_length=2, blank=True, null=True)
    x6 = models.CharField(max_length=2, blank=True, null=True)
    x7 = models.CharField(max_length=2, blank=True, null=True)
    x8 = models.CharField(max_length=2, blank=True, null=True)
    x9 = models.CharField(max_length=2, blank=True, null=True)
    x10 = models.CharField(max_length=2, blank=True, null=True)
    x11 = models.CharField(max_length=2, blank=True, null=True)
    x12 = models.CharField(max_length=2, blank=True, null=True)
    r = models.IntegerField(blank=True, null=True)
    h = models.IntegerField(blank=True, null=True)
    e = models.IntegerField(blank=True, null=True)
    b = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'score_record'






        
class TodayGameInfo(models.Model):
    game_idx = models.CharField(primary_key=True, max_length=14)
    home_name = models.CharField(max_length=3, blank=True, null=True)
    away_name = models.CharField(max_length=3, blank=True, null=True)
    stadium = models.CharField(max_length=2, blank=True, null=True)
    end = models.CharField(max_length=100,blank=True, null=True)
    etc = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'today_game_info'
                
class TodayTeamGameInfo(models.Model):
    #game_idx = models.CharField(max_length=14)
    game_idx = models.ForeignKey(TodayGameInfo, models.DO_NOTHING, db_column='game_idx', blank=True, null=True)
    team_game_idx = models.CharField(primary_key=True, max_length=9)
    #year = models.ForeignKey('TeamInfo', models.DO_NOTHING, db_column='year', blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    
    #team_num = models.ForeignKey('TeamInfo', models.DO_NOTHING, db_column='team_num', blank=True, null=True,related_name='todayteamgameinfo_team_num_set')
    team_num = models.IntegerField(blank=True, null=True)
    foe_num = models.IntegerField(blank=True, null=True)
    game_num = models.IntegerField(blank=True, null=True)
    home_away = models.CharField(max_length=4, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'today_team_game_info'
        ordering = ['game_idx','home_away']
class TodayLineUp(models.Model):
    
    team_game_idx = models.CharField(primary_key=True, max_length=9)
    bo = models.CharField(max_length=10,blank=True,null=True)
    
    po = models.CharField(max_length=10, blank=True, null=True)
    name = models.CharField(max_length=10, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'today_lineup'
        
class TodayToTo(models.Model):
    
    date = models.CharField(primary_key = True,max_length=8)
    time = models.CharField(max_length=5,blank=True,null=True)
    site_name = models.CharField(max_length=20,blank=True,null=True)
    win_type = models.IntegerField(blank=True,null=True)
    away_name = models.CharField(max_length=10,blank=True,null=True)
    home_name = models.CharField(max_length=10,blank=True,null=True)
    away_odds = models.FloatField(blank=True,null=True)
    home_odds = models.FloatField(blank=True,null=True)
    handicap = models.FloatField(blank=True,null=True)
    craw_time = models.CharField(max_length=5,blank=True,null=True)
    
    class Meta:
        managed = False
        db_table = 'today_toto'
        unique_together = (('date','time','site_name','win_type','away_name','home_name','craw_time'))
        
        
class RunGraphData(models.Model):
    
    team_game_idx = models.CharField(primary_key=True, max_length=9)
    #year = models.ForeignKey('TeamInfo', models.DO_NOTHING, db_column='year', blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    #team_num = models.ForeignKey('TeamInfo', models.DO_NOTHING, db_column='team_num', blank=True, null=True,related_name='graph_data_team_num_set')
    team_num = models.IntegerField(blank=True, null=True)
    game_num = models.IntegerField(blank=True, null=True)
    run_1 = models.FloatField(blank=True, null=True)
    run_5 = models.FloatField(blank=True, null=True)
    run_20 = models.FloatField(blank=True, null=True)
    rp_fip_5 = models.FloatField(blank=True, null=True)
    rp_fip_20 = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'run_graph_data'

class UpdateTime(models.Model):
    
    date = models.CharField(primary_key = True,max_length=8)
    craw_time = models.CharField(max_length=5,blank=True,null=True)
    craw_type = models.IntegerField(blank=True,null=True)
    
    class Meta:
        managed = False
        db_table = 'update_time'

class Post(models.Model):
    post_id = models.IntegerField(primary_key = True)
    user_id = models.ForeignKey(User, db_column = 'user_id', on_delete= models.DO_NOTHING)
    title = models.CharField(max_length=30)           # 게시물 제목
    content = models.TextField(max_length = 1000)                       # 게시물 내용
    created_at = models.DateTimeField(auto_now_add=True)  # 게시물 작성 시간
    updated_at = models.DateTimeField(auto_now=True)      # 게시물 수정 시간

    def __str__(self):
        return self.title
    class Meta:
        
        db_table = 'board_post'

class Comment(models.Model):
    comment_id = models.IntegerField(primary_key = True)
    user_id = models.ForeignKey(User, db_column = 'user_id', on_delete= models.DO_NOTHING)
    post_id = models.ForeignKey(Post, db_column = 'post_id', on_delete=models.CASCADE)  # 게시물 참조
    content = models.TextField()                        # 댓글 내용
    created_at = models.DateTimeField(auto_now_add=True)  # 댓글 작성 시간
    updated_at = models.DateTimeField(auto_now=True)      # 댓글 수정 시간

    def __str__(self):
        return f'Comment by {self.post.title}'
    class Meta:
        
        db_table = 'board_comment'