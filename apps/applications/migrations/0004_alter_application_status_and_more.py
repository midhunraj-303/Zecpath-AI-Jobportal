
from django.db import migrations, models


def migrate_application_statuses(apps, schema_editor):
    """
    Convert legacy application statuses to the new status values.
    """

    Application = apps.get_model('applications', 'Application')
    ApplicationStatusHistory = apps.get_model(
        'applications',
        'ApplicationStatusHistory'
    )

    database = schema_editor.connection.alias

    # Update application records.
    Application.objects.using(database).filter(
        status='PENDING'
    ).update(status='APPLIED')

    Application.objects.using(database).filter(
        status='ACCEPTED'
    ).update(status='SELECTED')

    # Update new status values in history.
    ApplicationStatusHistory.objects.using(database).filter(
        new_status='PENDING'
    ).update(new_status='APPLIED')

    ApplicationStatusHistory.objects.using(database).filter(
        new_status='ACCEPTED'
    ).update(new_status='SELECTED')

    # Update previous status values in history.
    ApplicationStatusHistory.objects.using(database).filter(
        previous_status='PENDING'
    ).update(previous_status='APPLIED')

    ApplicationStatusHistory.objects.using(database).filter(
        previous_status='ACCEPTED'
    ).update(previous_status='SELECTED')


def reverse_application_statuses(apps, schema_editor):
    """
    Restore legacy application status values during rollback.
    """

    Application = apps.get_model('applications', 'Application')
    ApplicationStatusHistory = apps.get_model(
        'applications',
        'ApplicationStatusHistory'
    )

    database = schema_editor.connection.alias

    Application.objects.using(database).filter(
        status='APPLIED'
    ).update(status='PENDING')

    Application.objects.using(database).filter(
        status='SELECTED'
    ).update(status='ACCEPTED')

    ApplicationStatusHistory.objects.using(database).filter(
        new_status='APPLIED'
    ).update(new_status='PENDING')

    ApplicationStatusHistory.objects.using(database).filter(
        new_status='SELECTED'
    ).update(new_status='ACCEPTED')

    ApplicationStatusHistory.objects.using(database).filter(
        previous_status='APPLIED'
    ).update(previous_status='PENDING')

    ApplicationStatusHistory.objects.using(database).filter(
        previous_status='SELECTED'
    ).update(previous_status='ACCEPTED')


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0003_applicationstatushistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='status',
            field=models.CharField(
                choices=[
                    ('APPLIED', 'Applied'),
                    ('REVIEWING', 'Reviewing'),
                    ('SHORTLISTED', 'Shortlisted'),
                    ('INTERVIEW_SCHEDULED', 'Interview Scheduled'),
                    ('REJECTED', 'Rejected'),
                    ('SELECTED', 'Selected'),
                ],
                default='APPLIED',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='applicationstatushistory',
            name='new_status',
            field=models.CharField(
                choices=[
                    ('APPLIED', 'Applied'),
                    ('REVIEWING', 'Reviewing'),
                    ('SHORTLISTED', 'Shortlisted'),
                    ('INTERVIEW_SCHEDULED', 'Interview Scheduled'),
                    ('REJECTED', 'Rejected'),
                    ('SELECTED', 'Selected'),
                ],
                help_text='New status assigned to the application.',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='applicationstatushistory',
            name='previous_status',
            field=models.CharField(
                blank=True,
                choices=[
                    ('APPLIED', 'Applied'),
                    ('REVIEWING', 'Reviewing'),
                    ('SHORTLISTED', 'Shortlisted'),
                    ('INTERVIEW_SCHEDULED', 'Interview Scheduled'),
                    ('REJECTED', 'Rejected'),
                    ('SELECTED', 'Selected'),
                ],
                help_text=(
                    'Status before the transition; '
                    'null for initial submission.'
                ),
                max_length=20,
                null=True,
            ),
        ),
        migrations.RunPython(
            migrate_application_statuses,
            reverse_application_statuses,
        ),
    ]
