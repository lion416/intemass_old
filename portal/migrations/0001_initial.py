# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TProfile'
        db.create_table('portal_tprofile', (
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('cellphone', self.gf('django.db.models.fields.CharField')(default='', max_length=16, null=True, blank=True)),
        ))
        db.send_create_signal('portal', ['TProfile'])

        # Adding M2M table for field classrooms on 'TProfile'
        m2m_table_name = db.shorten_name('portal_tprofile_classrooms')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tprofile', models.ForeignKey(orm['portal.tprofile'], null=False)),
            ('classroom', models.ForeignKey(orm['classroom.classroom'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tprofile_id', 'classroom_id'])

        # Adding model 'SProfile'
        db.create_table('portal_sprofile', (
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('cellphone', self.gf('django.db.models.fields.CharField')(default='', max_length=16, null=True, blank=True)),
            ('classroom', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['classroom.Classroom'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('teacher', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.TProfile'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('portal', ['SProfile'])


    def backwards(self, orm):
        # Deleting model 'TProfile'
        db.delete_table('portal_tprofile')

        # Removing M2M table for field classrooms on 'TProfile'
        db.delete_table(db.shorten_name('portal_tprofile_classrooms'))

        # Deleting model 'SProfile'
        db.delete_table('portal_sprofile')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'classroom.classroom': {
            'Meta': {'object_name': 'Classroom'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'roomname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'volume': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'portal.sprofile': {
            'Meta': {'object_name': 'SProfile'},
            'cellphone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'classroom': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['classroom.Classroom']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'teacher': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.TProfile']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'portal.tprofile': {
            'Meta': {'object_name': 'TProfile'},
            'cellphone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'classrooms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['classroom.Classroom']", 'symmetrical': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['portal']