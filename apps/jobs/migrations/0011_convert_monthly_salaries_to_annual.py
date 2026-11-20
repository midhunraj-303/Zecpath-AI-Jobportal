
from decimal import Decimal

from django.db import migrations
from django.db.models import F


def convert_monthly_salaries_to_annual(apps, schema_editor):
    """
    Convert existing monthly job salary ranges into annual INR amounts.

    Only records marked MONTH are converted, preventing double conversion.
    Null salary values remain unchanged.
    """

    Job = apps.get_model('jobs', 'Job')

    monthly_jobs = Job.objects.filter(salary_period='MONTH')

    monthly_jobs.update(
        salary_min=F('salary_min') * Decimal('12'),
        salary_max=F('salary_max') * Decimal('12'),
        salary_period='YEAR',
        salary_currency='INR',
    )


def reverse_annual_salary_conversion(apps, schema_editor):
    """
    Restore annual job salaries to monthly values during migration rollback.
    """

    Job = apps.get_model('jobs', 'Job')

    annual_jobs = Job.objects.filter(salary_period='YEAR')

    annual_jobs.update(
        salary_min=F('salary_min') / Decimal('12'),
        salary_max=F('salary_max') / Decimal('12'),
        salary_period='MONTH',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0010_alter_job_salary_period'),
    ]

    operations = [
        migrations.RunPython(
            convert_monthly_salaries_to_annual,
            reverse_code=reverse_annual_salary_conversion,
        ),
    ]
