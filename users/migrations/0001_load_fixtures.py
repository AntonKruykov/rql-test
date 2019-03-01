# Generated by Django 2.1.7 on 2019-03-01 12:28
from django.core.management import call_command
from django.db import migrations
from django.db.migrations.operations.base import Operation


class LoadFixture(Operation):
    reduces_to_sql = False
    reversible = True

    def __init__(self, *fixtures):
        self.fixtures = fixtures

    def state_forwards(self, app_label, state):
        pass

    def database_forwards(self, app_label, schema_editor, from_state,
                          to_state):
        for fixture in self.fixtures:
            call_command('loaddata', fixture, app_label=app_label)

    def database_backwards(self, app_label, schema_editor, from_state,
                           to_state):
        pass

    def describe(self):
        return "Load Fixture Operation"


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        LoadFixture('users'),
    ]
