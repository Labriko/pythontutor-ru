# -*- coding: utf-8 -*-

from django import template
from tutorial.models import Problem, Submission
from django.contrib.auth.models import User
from tutorial.load_problems import load_problem
from django.conf import settings


import urllib.request, urllib.parse, urllib.error
import cgi


register = template.Library()

ideal_user = User.objects.get(username='admin')

program_code_start = '<pre class="prettyprint lang-python">'
program_code_end = '</pre>'

LESSON_IMG_ROOT = '/pylernu/static/lesson_images/'


def _insert_code_into_url(code):
    return urllib.parse.quote(code.encode('utf-8'), '')


def _render_code_to_html(code, input_data='', context={}, executable=True, blockquote=True):
    if context.get("navigation", None):
        visualizer_link = template.Template(r"{% url visualizer_for_lesson " + "'{0}' '{1}'".\
            format(context.get('navigation')['course'].urlname, context.get('navigation')['lesson'].urlname) + " %}").render(context)
    else:
        visualizer_link = template.Template("r{% url visualizer %}").render(context)
    return (('''<blockquote>''' if blockquote else '') 
        + '''{program_code_start}{0}{program_code_end}''' 
        + ('''<a href="{1}?code={2}&input={3}">Показать код в визуализаторе</a>''' if executable else '')
        + ('''</blockquote>''' if blockquote else '')).format(cgi.escape(code), visualizer_link, _insert_code_into_url(code), _insert_code_into_url(input_data), **globals())



class ProgramCodeNode(template.Node):
    def __init__(self, nodelist, executable=True):
        self.nodelist = nodelist
        self.executable = executable

    def render(self, context):
        context['input_data'] = " "
        code = self.nodelist.render(context).strip()
        input_data = context.get("input_data", " ")
        return _render_code_to_html(code, input_data, context, self.executable)


@register.tag('program')
def highlight_program_code(parser, token):
    nodelist = parser.parse(('endprogram',))
    parser.delete_first_token()
    return ProgramCodeNode(nodelist, executable=True)


@register.tag('noprogram')
def highlight_program_code(parser, token):
    nodelist = parser.parse(('endnoprogram',))
    parser.delete_first_token()
    return ProgramCodeNode(nodelist, executable=False)


class InputDataNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        input_data = self.nodelist.render(context).strip()
        context["input_data"] = input_data
        return ''


@register.tag('inputdata')
def add_input_data(parser, token):
    nodelist = parser.parse(('endinputdata',))
    parser.delete_first_token()
    return InputDataNode(nodelist)


class ProblemLinkNode(template.Node):
    def __init__(self, problem_ref):
        self.problem_ref = problem_ref

    def render(self, context):
        problem_urlname = context[self.problem_ref]['urlname']
        problem = load_problem(Problem.objects.get(urlname=problem_urlname))
        user = context['request'].user
        if user.is_authenticated():
            statuses = [submission.get_status_display() for submission 
                    in Submission.objects.filter(user=user, problem=problem['db_object'])]
        else:
            statuses = []
        if 'ok' in statuses:
            css_class = 'okProblemLink'
        elif 'error' in statuses:
            css_class = 'errorProblemLink'
        else:
            css_class = 'unsubmittedProblemLink'
        return '<span class="{0}">{1}</span>'.format(css_class, problem['name'])


@register.tag('problem_link')
def get_problem_link(parser, token):
    try:
        tag_name, problem_ref = token.split_contents()
    except ValueError:
        msg = '{0} tag requires a single argument'.format(token.split_contents()[0])
        raise template.TemplateSyntaxError(msg)
    return ProblemLinkNode(problem_ref)



class IdealSolutionNode(template.Node):
    def __init__(self, problem_ref):
        self.problem_ref = problem_ref

    def render(self, context):
        problem_urlname = context[self.problem_ref]['urlname']
        problem = load_problem(Problem.objects.get(urlname=problem_urlname))
        user = context['request'].user
        if user.is_authenticated():
            user_solutions = [submission for submission 
                in Submission.objects.filter(user=user, problem=problem['db_object']).order_by('time')
                if submission.get_status_display() == 'ok']
        else:
            user_solutions = []
        ideal_solutions = [submission for submission 
                in Submission.objects.filter(user=ideal_user, problem=problem['db_object']).order_by('-time')
                if submission.get_status_display() == 'ok']
        if user_solutions and ideal_solutions:
            return '''
                <table border="1" class="userAndIdealSolutions">
                    <tr>
                        <td class="header">Ваше решение</td>
                        <td class="header">Эталонное решение</td>
                    </tr>
                    <tr>
                        <td class="body">
                        {user_solution}
                        </td>
                        <td class="body">
                        {ideal_solution}
                        </td>
                    </tr>
                </table>
                <br>
            '''.format(**dict(user_solution=_render_code_to_html(user_solutions[0].code, 
                                                                 input_data=problem['tests'][0], 
                                                                 context=context,
                                                                 executable=True,
                                                                 blockquote=False), 
                              ideal_solution=_render_code_to_html(ideal_solutions[0].code,
                                                                 input_data=problem['tests'][0],
                                                                 context=context,
                                                                 executable=True,
                                                                 blockquote=False), **globals()))
        else:
            return ''


@register.tag('ideal_solution')
def get_ideal_solution_link(parser, token):
    try:
        tag_name, problem_ref = token.split_contents()
    except ValueError:
        msg = '{0} tag requires a single argument'.format(token.split_contents()[0])
        raise template.TemplateSyntaxError(msg)
    return IdealSolutionNode(problem_ref)


class LessonNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        context['sections'] = []
        content = self.nodelist.render(context)
        sections = context.get("sections", [])
        html = ['<div class="lesson">']
        if 'section_counter' in context:
            html.append('<div class="sections">Содержание:')
            for i, name in enumerate(sections):
                html.append('<br><a href="#{0}">{1}</a>'.format(i, name))
            html.append('</div>\n')
        html.append(content)
        html.append('</div>')
        return ''.join(html)


@register.tag('lesson')
def wrap_lesson(parser, token):
    nodelist = parser.parse(('endlesson',))
    parser.delete_first_token()
    return LessonNode(nodelist)


class WrapperNode(template.Node):
    def __init__(self, nodelist, html_before, html_after):
        self.nodelist = nodelist
        self.html_before = html_before
        self.html_after = html_after

    def render(self, context):
        return (template.Template(str(self.html_before)).render(context) + 
                self.nodelist.render(context) + 
                template.Template(str(self.html_after)).render(context))


class SectionNode(WrapperNode):
    def __init__(self, nodelist, section_name):
        super(SectionNode, self).__init__(nodelist, 
                '<h3><a name="{0}">' + '{0}'.format(section_name) + '</a></h3>', '')
        self.section_name = section_name

    def render(self, context):
        if 'section_counter' not in context:
            context['section_counter'] = 0
        self.html_before = self.html_before.format(context['section_counter'])
        context['section_counter'] += 1
        context['sections'].append(self.section_name)
        return super(SectionNode, self).render(context)


class SingleNode(template.Node):
    def __init__(self, html):
        self.html = html

    def render(self, context):
        return template.Template(str(self.html)).render(context)


def create_wrapper_tag(name, html_before, html_after):
    @register.tag(name)
    def wrapper_tag_func(parser, token):
        nodelist = parser.parse(('end' + name,))
        parser.delete_first_token()
        return WrapperNode(nodelist, html_before, html_after)   


def create_parameterized_wrapper_tag(name, html_before, html_after):
    @register.tag(name)
    def wrapper_tag_func(parser, token):
        params = token.split_contents()[1:]
        nodelist = parser.parse(('end' + name,))
        parser.delete_first_token()
        try:
            return WrapperNode(nodelist, html_before.format(*[str(p)[1:-1] for p in params]), html_after)   
        except IndexError:
            raise IndexError("tag '{0}' doesn't have a required parameter".format(name))


def create_parameterized_single_tag(name, html):
    @register.tag(name)
    def wrapper_tag_func(parser, token):
        params = token.split_contents()[1:]
        try:
            return SingleNode(html.format(*[str(p)[1:-1] for p in params]))
        except IndexError:
            raise IndexError("tag '{0}' doesn't have a required parameter".format(name))


@register.tag('section')
def wrapper_tag_func(parser, token):
    params = token.split_contents()[1:]
    nodelist = parser.parse(('endsection',))
    parser.delete_first_token()
    try:
        return SectionNode(nodelist, str(params[0])[1:-1])
    except IndexError:
        raise IndexError("tag 'section' doesn't have a required parameter")


create_wrapper_tag('input', '<p class="example_header">Пример входных данных:<br><pre>', '</pre></p>')
create_wrapper_tag('output', '<p class="example_header">Пример выходных данных:<br><pre>', '</pre></p>')
create_wrapper_tag('smartsnippet', '<p><div class="smartsnippet">', '</div></p>')
create_wrapper_tag('newword', '<u>', '</u>')
create_wrapper_tag('theorem', '<p><b>Теорема. </b>', '</p>')
create_wrapper_tag('proof', '<p><i>Доказательство. </i>', ' &#x25ae;</p>')

# create_parameterized_wrapper_tag('section', u'<h3>{0}</h3>', '')
create_parameterized_wrapper_tag('subsection', '<h4>{0}</h4>', '')

create_parameterized_single_tag('img', '<p align="center"><img src="' + LESSON_IMG_ROOT + '{0}" width="{1}%"></p>')