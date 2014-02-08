# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


# currently totally unused model
class Language(models.Model):
    name = models.CharField('Внутреннее название языка', max_length=200, unique=True)

    def __unicode__(self):
        return self.name


class Problem(models.Model):
    urlname = models.CharField('Имя для адресной строки', max_length=200, unique=True, db_index=True)
    filename = models.CharField('Имя файла с задачей', max_length=200, blank=True)

    def __unicode__(self):
        return '{self.urlname}'.format(**locals())


class Lesson(models.Model):
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    # Currently description is nowhere viewed
    urlname = models.CharField('Имя для адресной строки', max_length=200, unique=True, db_index=True)
    filename = models.CharField('Имя файла с уроком', max_length=200, blank=True)
    problems = models.ManyToManyField(Problem, through='ProblemInLesson', blank=True, null=True)
    external_contest_link = models.CharField('Внешняя ссылка на контест', max_length=200, blank=True, null=True)

    def __unicode__(self):
        return '{self.urlname}: {self.title} (файл: {self.filename})'.format(**locals())

    def __le__(self, other):
        return self.id < other.id


class ProblemInLesson(models.Model):
    problem = models.ForeignKey(Problem)
    lesson = models.ForeignKey(Lesson)
    order = models.IntegerField()


class Course(models.Model):
    OK_AC_POLICY_CHOICES = (
        (0, 'just_ok'),
        (1, 'use_accepted_instead_of_ok'),
    )

    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    urlname = models.CharField('Имя для адресной строки', max_length=200, unique=True, db_index=True)
    lessons = models.ManyToManyField(Lesson, through='LessonInCourse', blank=True, null=True)
    language = models.ForeignKey(Language, blank=True, null=True)  # unused field
    ok_ac_policy = models.IntegerField(choices=OK_AC_POLICY_CHOICES)

    def __unicode__(self):
        return self.title


class LessonInCourse(models.Model):
    lesson = models.ForeignKey(Lesson)
    course = models.ForeignKey(Course)
    order = models.IntegerField()


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    # hidden = models.BooleanField(default=True)
    course = models.ForeignKey(Course, null=True, blank=True)
    # here you can add fields like 'school'

    def __unicode__(self):
        return '{0} {1} ({2})'.format(self.user.first_name, self.user.last_name, self.user.username)


class Submission(models.Model):
    STATUS_CHOICES = (
        (0, 'error'), # don't remove this value, or you will have a mess in your database!
        (1, 'ok'),
        (2, 'accepted'),
        (3, 'coding_style_violation'),
        (4, 'ignored'),
    )

    code = models.TextField()
    user = models.ForeignKey(User)
    problem = models.ForeignKey(Problem, db_index=True)
    status = models.IntegerField(choices=STATUS_CHOICES)
    time = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return '{self.user.first_name} {self.user.last_name} on {self.problem}: {0} ({self.time})'\
                .format(self.get_status_display(), **locals())
