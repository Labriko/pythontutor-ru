# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Lesson'
        db.create_table('tutorial_lesson', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('tutorial', ['Lesson'])

        # Adding model 'Course'
        db.create_table('tutorial_course', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('tutorial', ['Course'])

        # Adding model 'LessonInCourse'
        db.create_table('tutorial_lessonincourse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lesson', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutorial.Lesson'])),
            ('course', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutorial.Course'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('tutorial', ['LessonInCourse'])


    def backwards(self, orm):
        # Deleting model 'Lesson'
        db.delete_table('tutorial_lesson')

        # Deleting model 'Course'
        db.delete_table('tutorial_course')

        # Deleting model 'LessonInCourse'
        db.delete_table('tutorial_lessonincourse')


    models = {
        'tutorial.course': {
            'Meta': {'object_name': 'Course'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lessons': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['tutorial.Lesson']", 'through': "orm['tutorial.LessonInCourse']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'tutorial.lesson': {
            'Meta': {'object_name': 'Lesson'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'tutorial.lessonincourse': {
            'Meta': {'object_name': 'LessonInCourse'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tutorial.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lesson': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tutorial.Lesson']"}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['tutorial']