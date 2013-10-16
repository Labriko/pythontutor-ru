# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Problem'
        db.create_table('tutorial_problem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('urlname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('tutorial', ['Problem'])

        # Adding model 'ProblemInLesson'
        db.create_table('tutorial_probleminlesson', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('problem', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutorial.Problem'])),
            ('lesson', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tutorial.Lesson'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('tutorial', ['ProblemInLesson'])

        # Adding field 'Course.urlname'
        db.add_column('tutorial_course', 'urlname',
                      self.gf('django.db.models.fields.CharField')(default='1534', unique=True, max_length=200),
                      keep_default=False)

        # Adding field 'Lesson.urlname'
        db.add_column('tutorial_lesson', 'urlname',
                      self.gf('django.db.models.fields.CharField')(default='inout_and_arithmetic_operations', unique=True, max_length=200),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Problem'
        db.delete_table('tutorial_problem')

        # Deleting model 'ProblemInLesson'
        db.delete_table('tutorial_probleminlesson')

        # Deleting field 'Course.urlname'
        db.delete_column('tutorial_course', 'urlname')

        # Deleting field 'Lesson.urlname'
        db.delete_column('tutorial_lesson', 'urlname')


    models = {
        'tutorial.course': {
            'Meta': {'object_name': 'Course'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lessons': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['tutorial.Lesson']", 'null': 'True', 'through': "orm['tutorial.LessonInCourse']", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'urlname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'tutorial.lesson': {
            'Meta': {'object_name': 'Lesson'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'problems': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['tutorial.Problem']", 'null': 'True', 'through': "orm['tutorial.ProblemInLesson']", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'urlname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'tutorial.lessonincourse': {
            'Meta': {'object_name': 'LessonInCourse'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tutorial.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lesson': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tutorial.Lesson']"}),
            'order': ('django.db.models.fields.IntegerField', [], {})
        },
        'tutorial.problem': {
            'Meta': {'object_name': 'Problem'},
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'urlname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'})
        },
        'tutorial.probleminlesson': {
            'Meta': {'object_name': 'ProblemInLesson'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lesson': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tutorial.Lesson']"}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'problem': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tutorial.Problem']"})
        }
    }

    complete_apps = ['tutorial']