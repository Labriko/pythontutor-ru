# -*- coding: utf-8 -*-

import operator
import json
import functools
import collections

from django.shortcuts import render, redirect

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django import template
from django.contrib.auth.models import User
from django.conf import settings

from tutorial.models import Problem, Lesson, Course, UserProfile, Submission
from tutorial.forms import UserCreationForm, UserProfileForm

from visualizer.web_exec import exec_script_on_input
from visualizer.web_run_test import run_script_on_test_input
from tutorial.load_problems import load_problem, load_raw_problem
from tutorial.utils import get_submission_color, sign_by_status, color_by_status


# MAX_INSTRUCTIONS_LIMIT = 200
ABSOLUTE_PATH_TO_LESSONS = settings.ABSOLUTE_PREFIX + 'lessons/'


def dummy(request):
    return HttpResponse('dummy requested')


def get_sorted_problems(lesson):
    problems = [load_problem(problem) for problem in lesson.problems.all()]
    problems_with_order = [(problem, problem['db_object'].probleminlesson_set.get(lesson=lesson).order) for problem in problems]
    problems_with_order.sort(key=lambda x: x[1])
    return [problem for problem, order in problems_with_order]


def get_sorted_lessons(course):
    return [lic.lesson for lic in sorted(course.lessonincourse_set.all(), 
                                         key=operator.attrgetter('order'))]


def get_best_saved_code(user, problem_urlname):
    problem = Problem.objects.get(urlname=problem_urlname)
    submissions = Submission.objects.filter(user=user, problem=problem).order_by("-time")
    submission = None
    for s in submissions:
        if s.get_status_display() == 'ok':
            submission = s
            break
    if not submission and len(submissions) > 0:
        submission = submissions[0]
    if submission:
        return submission.code
    else:
        return u""


def need_login(function):
    @functools.wraps(function)
    def need_login_wrapper(*args, **kwargs):
        request = args[0]
        if settings.NEED_LOGIN and not request.user.is_authenticated():
            return redirect(settings.SERVER_PREFIX + 'accounts/login/')
        return function(*args, **kwargs)
    return need_login_wrapper


def need_admin(function):
    @functools.wraps(function)
    def need_admin_wrapper(*args, **kwargs):
        request = args[0]
        if not request.user.is_staff:
            return HttpResponseBadRequest(u'Необходимо быть администратором'.encode('utf-8'))
        return function(*args, **kwargs)
    return need_admin_wrapper


@need_login
def profile(request):
    errors = []
    messages = []
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data['new_password']:
                if data['new_password'] != data['new_password_repeated']:
                    errors.append('Новый пароль повторен неправильно')
                else:
                    request.user.set_password(data['new_password'])
                    messages.append('Пароль успешно изменен')
            if data['first_name'] and data['last_name']:
                request.user.first_name = data['first_name']
                request.user.last_name = data['last_name']
            else:
                errors.append('Имя и фамилия не могут быть пустыми')
            request.user.save()
    else:
        form = UserProfileForm(dict(first_name=request.user.first_name, last_name=request.user.last_name))
    return render(request, 'profile.html', locals())


def home(request):
    raw_courses = list(Course.objects.all())
    if request.user.is_authenticated():
        user_course = request.user.get_profile().course
    else:
        user_course = None
    lessons = {course: [lic for lic in sorted(course.lessonincourse_set.all(), 
                        key=operator.attrgetter('order'))]
                        for course in raw_courses}
    # lessons = {course: [lic.lesson for lic in sorted(course.lessonincourse_set.all(), 
    #                     key=operator.attrgetter('order'))]
    #                     for course in raw_courses}                        
    courses = sorted(lessons.items(), key=lambda x: x[0] != user_course)
    return render(request, 'index.html', locals())



def visualizer(request):
    return render(request, 'visualizer.html', locals())


def visualizer_for_lesson(request, course_name, lesson_name):
    course = Course.objects.get(urlname=course_name)
    lesson = Lesson.objects.get(urlname=lesson_name)
    navigation = dict(course=course, lesson=lesson)
    return render(request, 'visualizer.html', locals())


def execute(request):
    # AJAX request
    # method: POST
    # params: user_script, input_data
    post = request.POST
    if post.has_key('user_script') and post.has_key('input_data'):
        user_script = post['user_script']
        input_data = post['input_data']

        json = exec_script_on_input(user_script, input_data)

        return HttpResponse(json, mimetype='text/plain')                
    else:
        return HttpResponseBadRequest()


def run_test(request):
    # AJAX request
    # method: POST
    # params: user_script, test_input, test_answer
    post = request.POST
    if (post.has_key('user_script') 
            and post.has_key('test_input') 
            and post.has_key('test_answer')):
        user_script = post['user_script']
        test_input = post['test_input']
        test_answer = post['test_answer']

        json = run_script_on_test_input(user_script, test_input, test_answer)

        return HttpResponse(json, mimetype='text/plain')
    else:
        return HttpResponseBadRequest()    


def lesson_in_course(request, course_name, lesson_name):
    course = Course.objects.get(urlname=course_name)
    lesson = Lesson.objects.get(urlname=lesson_name)
    navigation = dict(course=course, lesson=lesson)
    lesson_in_course = lesson.lessonincourse_set.get(course=course)
    raw_lesson_content = open(ABSOLUTE_PATH_TO_LESSONS + lesson.filename, 'r').read().decode("utf-8")
    lesson_content = process_lesson_content(raw_lesson_content, course, lesson)
    problems = get_sorted_problems(lesson=lesson)
    return render(request, 'lesson.html', locals())


def process_lesson_content(raw, course=None, lesson=None):
    lesson_content = u'{% load tags %}\n{% lesson %}\n' + raw + '{% endlesson %}'
    t = template.Template(lesson_content)
    return t.render(template.Context(dict(navigation=dict(course=course, lesson=lesson))))


@need_login
def problem_in_lesson(request, course_name, lesson_name, problem_name):
    course = Course.objects.get(urlname=course_name)
    lesson = Lesson.objects.get(urlname=lesson_name)
    navigation = dict(course=course, lesson=lesson)
    
    # actually it's unused so far as problem loads dynamically by AJAX
    # problem = load_problem(Problem.objects.get(urlname=problem_name))

    return render(request, 'problem.html', locals())
    

def send_problem_to_frontend(request):
    # AJAX request
    # method: GET            
    # params: problem_urlname
    get = request.GET
    if get.has_key('problem_urlname'):
        problem_urlname = get['problem_urlname']

        problem = load_raw_problem(Problem.objects.get(urlname=problem_urlname))

        # we should fill this field by last submit, if any
        problem['savedCode'] = get_best_saved_code(request.user, problem['urlname'])

        output_json = json.dumps(problem)
        
        return HttpResponse(output_json, mimetype='text/plain')                
    else:
        return HttpResponseBadRequest()


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username):
                error = u'Пользователь с таким логином уже существует'
                return direct_to_template(request, 'register.html', locals())

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            
            user = User.objects.create_user(username, email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            user_profile = UserProfile(user=user)
            user_profile.save()

            return redirect(settings.SERVER_PREFIX + 'accounts/login/')

    form = UserCreationForm()
    return render(request, 'register.html', locals())


def post_grading_result(request):
    # AJAX request
    # method: POST
    # params: problem, code, result
    post = request.POST
    if (post.has_key('problem') and post.has_key('code') and post.has_key('result')
            and request.user.is_authenticated()):
        problem_urlname = post['problem']
        problem = Problem.objects.get(urlname=problem_urlname)
        code = post['code']
        status = post['result']
        user = request.user

    if user.get_profile().course and user.get_profile().course.get_ok_ac_policy_display() == 'use_accepted_instead_of_ok':
        if status == 'ok':
            status = 'accepted'

        submission = Submission(problem=problem, code=code, user=user, 
                                status={v: k for k, v in Submission.STATUS_CHOICES}[status])

        submission.save()

        return HttpResponse(json, mimetype='text/plain')                
    else:
        return HttpResponseBadRequest()


def standings_for_lesson(request, course_urlname, lesson_urlname):
    course = Course.objects.get(urlname=course_urlname)
    lesson = Lesson.objects.get(urlname=lesson_urlname)
    navigation = dict(course=course, lesson=lesson)
    return standings_for_lessons(request, course, [lesson], navigation)


def standings_for_course(request, course_urlname):
    course = Course.objects.get(urlname=course_urlname)
    lessons = get_sorted_lessons(course)
    navigation = dict(course=course)
    return standings_for_lessons(request, course, lessons, navigation)


def get_users_and_best_submissions_for_problems(course, problems_loaded):
    users = {user_profile.user for user_profile in course.userprofile_set.select_related().all()}
    submissions = {} # key: (user, problem)
    problems_db_objects = {problem['db_object'] for problem in problems_loaded}
    for submission in Submission.objects.select_related().all().order_by('time'):
        # # we assume there are only two submission statuses: 'error' and 'ok'.
        # # for every (user, problem) we find chronologically first 'ok' submit.
        # # if absent, we find chronologically last 'error' submit.
        # if submission.problem in problems_db_objects and submission.user in users:
        #     problem = submission.problem
        #     user = submission.user
        #     if (user, problem) in submissions:
        #         prev_submission = submissions[(user, problem)]
        #         if prev_submission.get_status_display() == 'error':  
        #             submissions[(user, problem)] = submission
        #     else:
        #         submissions[(user, problem)] = submission

        # we assume there are following submission statuses: 'ok', 'error', 'accepted',
        # 'coding_style_violation', 'ignored'.
        # for every (user, problem) we find chronologically first 'ok' submit.
        # if absent, we find chronologically last 'accepted' submit.
        # if absent, we find chronologically last 'error', 'coding_style_violation' 
        #                                                  or 'ignored' submit.
        if submission.problem in problems_db_objects and submission.user in users:
            problem = submission.problem
            user = submission.user
            if (user, problem) in submissions:
                prev_submission = submissions[(user, problem)]
                if (prev_submission.get_status_display() not in ['ok', 'accepted']
                        or (prev_submission.get_status_display() == 'accepted' 
                        and submission.get_status_display() in ['accepted', 'ok'])):
                    submissions[(user, problem)] = submission
            else:
                submissions[(user, problem)] = submission                
    return users, submissions


def standings_for_lessons(request, course, lessons, navigation):
    problems = []

    for lesson in lessons:
        problems.extend(get_sorted_problems(lesson))

    users, submissions = get_users_and_best_submissions_for_problems(course, problems)

    user_scores = {user: [0, 0, 0] for user in users}  # [num_solved, rating, num_attempted]

    problems_num_solved = collections.defaultdict(int)
    for (user, problem_db_object), submission in submissions.items():
        if submission.get_status_display() == 'ok':
            problems_num_solved[problem_db_object] += 1

    for (user, problem_db_object), submission in submissions.items():
        if submission.get_status_display() == 'ok':
            user_scores[user][0] += 1
            user_scores[user][1] += len(users) - problems_num_solved[problem_db_object] + 1
        else:
            user_scores[user][2] += 1

    users = list(users)
    users.sort(key=lambda x: ([-y for y in user_scores[x]], x.last_name, x.first_name))
    standings = {}
    for user in users:
        standings[user] = []
        for problem in problems:
            submission = submissions.get((user, problem['db_object']), None)
            if submission:                                               
                color = color_by_status[submission.get_status_display()]
                sign = sign_by_status[submission.get_status_display()]
                standings[user].append((color, get_submission_color(color), sign, problem, submission))
            else:
                standings[user].append(('white', '#ffffff', '', problem, None))
    users = [(user, standings[user], user_scores[user][0], user_scores[user][1]) for user in users if user_scores[user][0] > 0]
    return render(request, 'standings.html', locals())


# All that comes after this line is a stub for a new functionality.
# For example, I wanted to visualize course success of kids in a more informative way.
# I also wanted to create a page with submissions constantly updated 
# to watch for the contest right during the lesson.
#
# Unfortunately, I abandoned all these ideas.


def course_success(request, course_urlname):
    # step #1. retrieve list of all lessons and number of problems in them
    # step #2. retrieve all submissions and for every pair 
    course = Course.objects.all(urlname=course_urlname)
    lessons = get_sorted_lessons(course)
    pass


@need_admin
def submissions_for_course(request, course_urlname):
    course = Course.objects.get(urlname=course_urlname)
    lessons = get_sorted_lessons(course)
    return redirect(settings.SERVER_PREFIX + 'teacher_statistics/submissions/for_lessons/' 
            + ','.join(lesson.urlname for lesson in lessons))


@need_admin
def submissions_for_lessons(request, lessons_comma_separated_list):
    return render(request, 'submissions.html', locals())


@need_admin
def init_lessons_info(request):
    # AJAX request
    # method: GET
    # params: lessons_comma_separated_list
    get = request.GET
    if get.has_key("lessons_comma_separated_list"):
        lessons = [Lesson.objects.get(urlname=s) for s in get["lessons_comma_separated_list"].split('%2C')]
        dict_lessons = [dict(urlname=lesson.urlname, title=lesson.title) for lesson in lessons]
        output_json = json.dumps(dict_lessons)
        return HttpResponse(output_json, mimetype='text/plain') 
    else:
        return HttpResponseBadRequest()


@need_admin
def get_new_submissions(request):
    # AJAX request
    # method: GET
    # params: lesson_urlname, last_retrieved_submission
    get = request.GET
    if get.has_key("lesson") and get.has_key("last_retrieved_submission"):
        pass
    else:
        return HttpResponseBadRequest()
