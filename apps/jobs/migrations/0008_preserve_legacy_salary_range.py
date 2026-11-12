
from django.db import migrations
from django.db.models import F


def preserve_legacy_salary_range(apps, schema_editor):
    """
    Copy legacy salary into both range boundaries when
    the new salary range has not already been populated.
    """

    Job = apps.get_model('jobs', 'Job')

    Job.objects.filter(
        salary__isnull=False,
        salary_min__isnull=True,
        salary_max__isnull=True
    ).update(
        salary_min=F('salary'),
        salary_max=F('salary')
    )


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_standardize_job_salary'),
    ]

    operations = [
        migrations.RunPython(
            preserve_legacy_salary_range,
            reverse_code=migrations.RunPython.noop
        ),
    ]
