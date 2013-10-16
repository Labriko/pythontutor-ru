# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect

from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django import template

import subprocess
import os

def resistors(request):
    if request.GET.get('upperleft'):
        coefficients = ['upperleft', 'lowerleft', 'middle', 'upperright', 'lowerright']
        for c in coefficients:
            locals()[c] = request.GET.get(c)
        input_data = '''4 5
1 2 {upperleft}
1 3 {lowerleft}
2 3 {middle}
2 4 {upperright}
3 4 {lowerright}'''.format(**locals())
        os.chdir('/var/www/pylernu/misc/')
        solver_process = subprocess.Popen(args=['./makar_solution'], 
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=open(os.devnull, 'w'))
        solution = solver_process.communicate(bytes(input_data))[0]
        try:
            numerator, denominator = solution.split()[1].split('/')
        except:
            pass
        print >> open('all_requests.txt', 'a'), request
    return render(request, 'resistors.html', locals())
