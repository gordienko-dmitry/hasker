# Generated by Django 2.1.5 on 2019-01-30 20:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userwithavatar',
            name='user',
        ),
        migrations.AlterField(
            model_name='answer',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Author'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Publication date'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='questions.Question', verbose_name='Question'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='rank',
            field=models.IntegerField(db_index=True, default=0, verbose_name='Rank'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='text',
            field=models.CharField(max_length=2000, verbose_name='Text'),
        ),
        migrations.AlterField(
            model_name='question',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Author'),
        ),
        migrations.AlterField(
            model_name='question',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Publication date'),
        ),
        migrations.AlterField(
            model_name='question',
            name='rank',
            field=models.IntegerField(default=0, verbose_name='Rank'),
        ),
        migrations.AlterField(
            model_name='question',
            name='right_answer',
            field=models.IntegerField(null=True, verbose_name='Right answer'),
        ),
        migrations.AlterField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(to='questions.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.CharField(max_length=2000, verbose_name='Text'),
        ),
        migrations.AlterField(
            model_name='question',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='text',
            field=models.CharField(error_messages={'unique': 'A tag with that text already exists.'}, max_length=50, unique=True, verbose_name='Tag'),
        ),
        migrations.AlterField(
            model_name='votesanswer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='votesanswer',
            name='voter_entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.Answer', verbose_name='Answer'),
        ),
        migrations.AlterField(
            model_name='votesquestion',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AlterField(
            model_name='votesquestion',
            name='voter_entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.Question', verbose_name='Question'),
        ),
        migrations.DeleteModel(
            name='UserWithAvatar',
        ),
    ]
