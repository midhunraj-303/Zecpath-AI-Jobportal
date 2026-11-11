from django.db import migrations, models


def migrate_existing_job_data(apps, schema_editor):
    """
    Migrate existing job records to the new schema.
    """

    Job = apps.get_model('jobs', 'Job')

    # Preserve existing salary amounts.
    Job.objects.filter(salary__isnull=False).update(
        salary_min=models.F('salary'),
        salary_max=models.F('salary')
    )

    # Map existing active jobs to PUBLISHED.
    Job.objects.filter(is_active=True).update(
        status='PUBLISHED'
    )

    # Map existing inactive jobs to PAUSED.
    Job.objects.filter(is_active=False).update(
        status='PAUSED'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('employers', '0002_employer_company_domain_employer_company_size_and_more'),
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('skill_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('skill_name', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='job',
            name='application_deadline',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='benefits',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='job',
            name='max_experience',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='min_experience',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=4),
        ),
        migrations.AddField(
            model_name='job',
            name='published_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='qualifications',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='responsibilities',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='salary_currency',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='salary_max',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='salary_min',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='salary_period',
            field=models.CharField(blank=True, choices=[('YEAR', 'Per Year'), ('MONTH', 'Per Month'), ('HOUR', 'Per Hour')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('PUBLISHED', 'Published'), ('PAUSED', 'Paused'), ('CLOSED', 'Closed'), ('EXPIRED', 'Expired')], default='DRAFT', max_length=20),
        ),
        migrations.AddField(
            model_name='job',
            name='vacancies',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.RunPython(
            migrate_existing_job_data,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name='job',
            name='employment_type',
            field=models.CharField(choices=[('FULL_TIME', 'Full Time'), ('PART_TIME', 'Part Time'), ('CONTRACT', 'Contract'), ('INTERNSHIP', 'Internship'), ('TEMPORARY', 'Temporary'), ('FREELANCE', 'Freelance')], default='FULL_TIME', max_length=20),
        ),
        migrations.AddField(
            model_name='job',
            name='skills',
            field=models.ManyToManyField(blank=True, related_name='jobs', to='jobs.skill'),
        ),
        migrations.AddConstraint(
            model_name='job',
            constraint=models.CheckConstraint(condition=models.Q(('max_experience__isnull', True), ('min_experience__lte', models.F('max_experience')), _connector='OR'), name='job_experience_range_valid'),
        ),
        migrations.AddConstraint(
            model_name='job',
            constraint=models.CheckConstraint(condition=models.Q(('salary_min__isnull', True), ('salary_max__isnull', True), ('salary_min__lte', models.F('salary_max')), _connector='OR'), name='job_salary_range_valid'),
        ),
    ]
