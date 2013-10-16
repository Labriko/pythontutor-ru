# -*- coding: utf-8 -*-

from django import forms


class UserCreationForm(forms.Form):
    username = forms.CharField(label='Логин')
    email = forms.CharField(label='Почта')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    first_name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилия')


class UserProfileForm(forms.Form):
    first_name = forms.CharField(label='Имя', required=True)
    last_name = forms.CharField(label='Фамилия', required=True)
    new_password = forms.CharField(label='Новый пароль', widget=forms.PasswordInput, 
        help_text="Заполните, чтобы поменять пароль, или оставьте поле пустым", required=False)
    new_password_repeated = forms.CharField(label='Новый пароль ещё раз', widget=forms.PasswordInput, required=False)
