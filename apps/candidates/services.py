
"""
Services for candidate job recommendations.
"""

from apps.jobs.models import Job
from rest_framework import serializers
from datetime import date

def normalize_skills(skills):
    """
    Convert a collection of skills into normalized skill names.

    Args:
        skills: An iterable of skill names.

    Returns:
        set: Unique, lowercase skill names.
    """

    return {
        skill.strip().casefold()
        for skill in skills
        if skill and skill.strip()
    }


def get_candidate_skills(candidate):
    """
    Extract and normalize skills from a candidate profile.

    Args:
        candidate: Candidate model instance.

    Returns:
        set: Normalized candidate skills.
    """

    candidate_skills = candidate.skills.split(',')

    return normalize_skills(candidate_skills)



def calculate_candidate_experience(candidate):
    """
    Calculate total professional experience in years.

    Overlapping employment periods are counted only once.
    Current employment uses today's date as its end date.

    Returns:
        float or None: Total experience in years.
        None if the candidate has no experience records.
    """

    experiences = candidate.experiences.all()

    if not experiences.exists():
        return None

    today = date.today()
    date_ranges = []

    for experience in experiences:

        start_date = experience.start_date

        end_date = (
            today
            if experience.is_current
            else experience.end_date
        )

        if end_date is None:
            continue

        if end_date < start_date:
            continue

        date_ranges.append((start_date, end_date))

    if not date_ranges:
        return None

    # Sort employment periods by their start date.
    date_ranges.sort(key=lambda period: period[0])

    merged_ranges = []

    for start_date, end_date in date_ranges:

        if not merged_ranges:
            merged_ranges.append([start_date, end_date])
            continue

        previous_start, previous_end = merged_ranges[-1]

        if start_date <= previous_end:
            merged_ranges[-1][1] = max(
                previous_end,
                end_date
            )
        else:
            merged_ranges.append([start_date, end_date])

    total_days = sum(
        (end_date - start_date).days
        for start_date, end_date in merged_ranges
    )

    return round(total_days / 365.25, 2)



def calculate_experience_match(
    candidate_experience,
    min_experience,
    max_experience
):
    """
    Calculate compatibility between candidate experience
    and job experience requirements.

    Returns:
        float or None: Experience compatibility percentage.
    """

    if candidate_experience is None:
        return None

    if min_experience is None and max_experience is None:
        return None

    if min_experience is None:
        min_experience = 0

    # No upper limit means experience above the minimum is acceptable.
    if max_experience is None:
        return (
            100.0
            if candidate_experience >= min_experience
            else round(
                (candidate_experience / min_experience) * 100,
                2
            ) if min_experience > 0 else 100.0
        )

    if min_experience <= candidate_experience <= max_experience:
        return 100.0

    if candidate_experience < min_experience:
        if min_experience == 0:
            return 100.0

        return round(
            (candidate_experience / min_experience) * 100,
            2
        )

    # Experience exceeds the maximum requirement.
    return 100.0


def calculate_location_match(candidate_location, job_location, work_mode):
    """
    Calculate location compatibility between a candidate and a job.

    Scoring:
        Remote job: 100%
        Exact city match: 100%
        Same state, different city: 60%
        Different state: 0%
        Missing location: None
    """

    if work_mode == 'REMOTE':
        return 100.0

    if not candidate_location or not job_location:
        return None

    candidate_parts = [
        part.strip().casefold()
        for part in candidate_location.split(',')
    ]

    job_parts = [
        part.strip().casefold()
        for part in job_location.split(',')
    ]

    if not candidate_parts or not job_parts:
        return None

    candidate_city = candidate_parts[0]
    job_city = job_parts[0]

    if candidate_city == job_city:
        return 100.0

    if len(candidate_parts) >= 2 and len(job_parts) >= 2:
        candidate_state = candidate_parts[1]
        job_state = job_parts[1]

        if candidate_state == job_state:
            return 60.0

        return 0.0

    return None



def calculate_skill_match(candidate_skills, job_skills):
    """
    Calculate the percentage of job-required skills
    that match the candidate's skills.

    Args:
        candidate_skills: Set of candidate skills.
        job_skills: Set of required job skills.

    Returns:
        dict: Match percentage and matched/missing skills.
    """

    if not job_skills:
        return {
            'match_percentage': None,
            'matched_skills': [],
            'missing_skills': [],
        }

    matched_skills = candidate_skills.intersection(job_skills)
    missing_skills = job_skills.difference(candidate_skills)

    match_percentage = round(
        (len(matched_skills) / len(job_skills)) * 100,
        2
    )

    return {
        'match_percentage': match_percentage,
        'matched_skills': sorted(matched_skills),
        'missing_skills': sorted(missing_skills),
    }



def calculate_salary_match(candidate_salary, job_salary_min, job_salary_max):
    """
    Calculate salary compatibility between a candidate and a job.

    All salary values are annual INR amounts.

    Returns:
        float or None: Salary compatibility percentage.
    """

    if candidate_salary is None:
        return None

    if job_salary_min is None and job_salary_max is None:
        return None

    # Use the available salary boundary if one is missing.
    if job_salary_min is None:
        job_salary_min = job_salary_max

    if job_salary_max is None:
        job_salary_max = job_salary_min

    if candidate_salary <= 0:
        return None

    # Job maximum meets or exceeds candidate expectation.
    if job_salary_max >= candidate_salary:
        return 100.0

    # Job maximum is below candidate expectation.
    salary_ratio = job_salary_max / candidate_salary

    return round(float(salary_ratio * 100), 2)




def calculate_overall_match(
    skill_match,
    experience_match,
    salary_match,
    location_match
):
    """
    Calculate the weighted overall job recommendation score.

    Weights:
        Skills: 50%
        Experience: 20%
        Salary: 20%
        Location: 10%

    Missing scores are excluded and the remaining weights
    are proportionally normalized.
    """

    scores = {
        'skills': (skill_match, 50),
        'experience': (experience_match, 20),
        'salary': (salary_match, 20),
        'location': (location_match, 10),
    }

    weighted_total = 0
    available_weight = 0

    for score, weight in scores.values():
        if score is not None:
            weighted_total += score * weight
            available_weight += weight

    if available_weight == 0:
        return None

    return round(weighted_total / available_weight, 2)


def get_recommended_jobs(candidate):
    """
    Find published jobs matching the candidate's skills.

    Jobs without required skills are excluded from recommendations.
    """

    candidate_skills = get_candidate_skills(candidate)

    candidate_experience = calculate_candidate_experience(
        candidate
    )

    jobs = Job.objects.filter(
        status='PUBLISHED',
        is_active=True,
        is_deleted=False,
    ).prefetch_related('skills', 'employer')

    recommendations = []

    for job in jobs:

        job_skills = normalize_skills(
            job.skills.filter(
                is_active=True,
                approval_status='APPROVED'
            ).values_list('skill_name', flat=True)
        )

        if not job_skills:
            continue

        match_data = calculate_skill_match(
            candidate_skills,
            job_skills
        )


        if match_data['match_percentage'] > 0:

            salary_match_percentage = calculate_salary_match(
                candidate.expected_salary_annual,
                job.salary_min,
                job.salary_max
            )

            experience_match_percentage = calculate_experience_match(
                candidate_experience,
                job.min_experience,
                job.max_experience
            )

            location_match_percentage = calculate_location_match(
                candidate.location,
                job.location,
                job.work_mode
            )

            overall_match_percentage = calculate_overall_match(
                skill_match=match_data['match_percentage'],
                experience_match=experience_match_percentage,
                salary_match=salary_match_percentage,
                location_match=location_match_percentage
            )


            recommendations.append({
                'job': job,
                **match_data,
                'salary_match_percentage': salary_match_percentage,
                'experience_match_percentage':experience_match_percentage,
                'location_match_percentage': location_match_percentage,
                'overall_match_percentage': overall_match_percentage,
            })


    recommendations.sort(
        key=lambda item: item['overall_match_percentage'],
        reverse=True
    )

    return recommendations




class RecommendedJobSerializer(serializers.ModelSerializer):
    """
    Serialize recommended jobs with skill-match information.
    """

    company_name = serializers.CharField(
        source='employer.company_name',
        read_only=True
    )

    required_skills = serializers.SerializerMethodField()

    class Meta:

        model = Job

        fields = [
            'job_id',
            'job_title',
            'company_name',
            'location',
            'employment_type',
            'work_mode',
            'min_experience',
            'max_experience',
            'salary_min',
            'salary_max',
            'required_skills',
        ]

    def get_required_skills(self, obj):
        """
        Return approved required skills for a job.
        """

        return list(
            obj.skills.filter(
                is_active=True,
                approval_status='APPROVED'
            ).values_list('skill_name', flat=True)
        )
