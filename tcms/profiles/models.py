# -*- coding: utf-8 -*-
from django.db import models

from tcms.core.models import TCMSContentTypeBaseModel


class Profiles(models.Model):
    userid = models.AutoField(primary_key=True)
    login_name = models.CharField(max_length=255, unique=True)
    cryptpassword = models.CharField(max_length=128, blank=True)
    realname = models.CharField(max_length=255)
    disabledtext = models.TextField()
    disable_mail = models.IntegerField(default=0)
    mybugslink = models.IntegerField()
    extern_id = models.IntegerField(blank=True)

    class Meta:
        db_table = u'profiles'

    def get_groups(self):
        q = UserGroupMap.objects.filter(user__userid=self.userid)
        q = q.select_related()
        groups = [assoc.group for assoc in q.all()]
        return groups


class Groups(models.Model):
    name = models.CharField(unique=True, max_length=255)
    description = models.TextField()
    isbuggroup = models.IntegerField()
    userregexp = models.TextField()
    isactive = models.IntegerField()

    class Meta:
        db_table = u'groups'


class UserGroupMap(models.Model):
    user = models.ForeignKey(Profiles)  # user_id
    # (actually has two primary keys)
    group = models.ForeignKey(Groups)  # group_id
    isbless = models.IntegerField(default=0)
    grant_type = models.IntegerField(default=0)

    class Meta:
        db_table = u'user_group_map'
        unique_together = ('user', 'group')


#
# Extra information for users
#


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', unique=True, related_name='profile')
    phone_number = models.CharField(blank=True, default='', max_length=128)
    url = models.URLField(blank=True, default='')
    im = models.CharField(blank=True, default='', max_length=128)
    im_type_id = models.IntegerField(blank=True, default=1, null=True)
    address = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = u'tcms_user_profiles'

    def get_im(self):
        from forms import IM_CHOICES

        if not self.im:
            return None

        for c in IM_CHOICES:
            if self.im_type_id == c[0]:
                return '[%s] %s' % (c[1], self.im)

    @classmethod
    def get_user_profile(cls, user):
        return cls.objects.get(user=user)

#
# TCMS Bookmarks in profile models
#


class BookmarkCategory(models.Model):
    user = models.ForeignKey('auth.User')
    name = models.CharField(max_length=1024)

    class Meta:
        db_table = u'tcms_bookmark_categories'

    def __unicode__(self):
        return self.name


class Bookmark(TCMSContentTypeBaseModel):
    user = models.ForeignKey('auth.User')
    category = models.ForeignKey(BookmarkCategory, blank=True, null=True,
                                 related_name='bookmark')
    name = models.CharField(max_length=1024)
    description = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=8192)

    class Meta:
        db_table = u'tcms_bookmarks'
        index_together = (('content_type', 'object_pk', 'site'),)

    def __unicode__(self):
        return self.name
