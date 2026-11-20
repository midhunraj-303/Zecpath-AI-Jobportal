
from decimal import Decimal

from django.db import migrations
from django.db.models import F


def convert_candidate_salary_to_annual(apps, schema_editor):
    """
    Convert existing candidate expected salaries from monthly to annual.

    Null values remain unchanged.
    """

    Candidate = apps.get_model('candidates', 'Candidate')

    Candidate.objects.filter(
        expected_salary_annual__isnull=False
    ).update(
        expected_salary_annual=(
            F('expected_salary_annual') * Decimal('12')
        )
    )


def reverse_candidate_salary_conversion(apps, schema_editor):
    """
    Restore candidate expected salaries to monthly values.
    """

    Candidate = apps.get_model('candidates', 'Candidate')

    Candidate.objects.filter(
        expected_salary_annual__isnull=False
    ).update(
        expected_salary_annual=(
            F('expected_salary_annual') / Decimal('12')
        )
    )


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0004_rename_expected_salary_candidate_expected_salary_annual'),
    ]

    operations = [
        migrations.RunPython(
            convert_candidate_salary_to_annual,
            reverse_code=reverse_candidate_salary_conversion,
        ),
    ]
