from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin, auth
admin.autodiscover()

from django.contrib.auth.views import login, logout

from tutorial.views import (dummy, home, visualizer, execute, lesson_in_course,
        problem_in_lesson, send_problem_to_frontend, run_test, register_user, post_grading_result,
        standings_for_lesson, visualizer_for_lesson, profile, course_success, submissions_for_lessons,
        submissions_for_course, standings_for_course,)

#from tutorial.misc.views import resistors


from django.conf import settings


urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', home, name="home"),
    
    url(r'^visualizer/for_course/([^/]+)/for_lesson/([^/]+)/', visualizer_for_lesson, name='visualizer_for_lesson'),

    url(r'^visualizer/', visualizer, name='visualizer'),

    url(r'^execute/', execute),

    url(r'^courses/$', dummy, name='courses'),

    url(r'^courses/([^/]+)/lessons/([^/]+)/$', lesson_in_course, name="lesson_in_course"),

    url(r'^courses/([^/]+)/lessons/([^/]+)/problems/([^/]+)/$', problem_in_lesson, name="problem_in_lesson"),

    url(r'^courses/([^/]+)/lessons/([^/]+)/standings/$', standings_for_lesson),    

    url(r'^courses/([^/]+)/standings/$', standings_for_course),    

    url(r'^load_problem/$', send_problem_to_frontend),

    url(r'^run_test/$', run_test),

    url(r'^accounts/login/$', login, {'template_name': 'login.html'}, name='login'),

    url(r'^accounts/logout/$', logout, {'next_page': settings.LOGIN_REDIRECT_URL}, name="logout"),

    url(r'^accounts/register/$', register_user, name='register'),

    url(r'^accounts/profile/$', profile, name='profile'),

    url(r'^tutorial/post_grading_result/$', post_grading_result),

    url(r'^teacher_statistics/course_success/([^/]+)/$', course_success, name='course_success'),

    url(r'^teacher_statistics/submissions/for_lessons/([^/]+)/$', submissions_for_lessons, name='submissions_for_lessons'),  

    url(r'^teacher_statistics/submissions/for_course/([^/]+)/$', submissions_for_course, name='submissions_for_course'),
    # example of use:
    # teacher_statistics/submissions/for_lessons/ifelse,for_loop/
)
