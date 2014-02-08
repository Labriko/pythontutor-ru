# -*- coding: utf-8 -*-

from tutorial import models

from django.contrib import admin

from django.contrib.auth.models import User

import operator


class ProblemInLessonInline(admin.TabularInline):
    model = models.ProblemInLesson
    extra = 5


class LessonInCourseInline(admin.TabularInline):
    model = models.LessonInCourse
    extra = 5


class LanguageAdmin(admin.ModelAdmin):
    pass


class ProblemAdmin(admin.ModelAdmin):
    pass


class LessonAdmin(admin.ModelAdmin):
    inlines = (ProblemInLessonInline,)


class CourseAdmin(admin.ModelAdmin):
    inlines = (LessonInCourseInline,)


def submission_sort_key(user, last_name, count):
    return last_name if count else chr(0xffff)


class NameSurnameListFilter(admin.SimpleListFilter):
    title = 'name surname'

    parameter_name = 'name_surname'

    def lookups(self, request, model_admin):
        users_with_submission_count = [(user, user.last_name, user.submission_set.count()) for user in User.objects.prefetch_related().all()]
        users_with_submission_count.sort(key=submission_sort_key)
        users = zip(*users_with_submission_count)[0]
        return [(user.username, '{1} {0} ({2}) [{3}]'.format(user.first_name, user.last_name, user.username, user.submission_set.count())) for user in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__username=self.value())
        else:
            return queryset.all()


class CourseListFilter(admin.SimpleListFilter):
    title = 'course'

    parameter_name = 'course'

    def lookups(self, request, model_admin):
        courses = models.Course.objects.all()
        return [(course.urlname, course.title) for course in courses]

    def queryset(self, request, queryset):
        if self.value():
            queryset = queryset.exclude(user__userprofile__course=None)
            for course in models.Course.objects.all().exclude(urlname=self.value()):
                queryset = queryset.exclude(user__userprofile__course=course)
            return queryset.all()
        else:
            return queryset.all()


def make_ok(modeladmin, requst, queryset):
    queryset.update(status=1) # should be code for 'ok'!
make_ok.short_description = 'Поставить ok выбранным посылкам'


def make_accepted(modeladmin, requst, queryset):
    queryset.update(status=2) # should be code for 'accepted'!
make_accepted.short_description = 'Поставить accepted выбранным посылкам'


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'name_surname', 'problem', 'status', 'time')
    list_filter = (CourseListFilter, 'status', NameSurnameListFilter, 'problem')
    actions = [make_ok, make_accepted]

    def name_surname(self, submission):
        return '{0} {1}'.format(submission.user.first_name, submission.user.last_name)

    name_surname.short_description = 'Name Surname'


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'course')
    list_filter = ('course',)
    list_editable = ('course',)


admin.site.register(models.Language, LanguageAdmin)
admin.site.register(models.Problem, ProblemAdmin)
admin.site.register(models.Lesson, LessonAdmin)
admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Submission, SubmissionAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
# admin.site.register(models.LessonInCourse)
