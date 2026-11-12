from django.db import migrations


def standardize_job_salary(apps, schema_editor):
    """
    Standardize all existing job salary metadata to INR per month.

    Preserve existing salary_min, salary_max and legacy salary values.
    """

    Job = apps.get_model('jobs', 'Job')

    Job.objects.all().update(
        salary_currency='INR',
        salary_period='MONTH'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_alter_job_salary_currency_alter_job_salary_period'),
    ]

    operations = [
        migrations.RunPython(
            standardize_job_salary,
            reverse_code=migrations.RunPython.noop
        ),
    ]