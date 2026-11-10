
from rest_framework import serializers

from .models import Candidate, Education, Experience
from pathlib import Path
from zipfile import BadZipFile, ZipFile


class EducationSerializer(serializers.ModelSerializer):
    """Serialize and validate a candidate's education record."""

    class Meta:
        """Define the education fields exposed through the API."""

        model = Education

        fields = [
            'id',
            'institution',
            'degree',
            'field_of_study',
            'start_year',
            'end_year',
            'grade',
        ]

        read_only_fields = ['id']

    def validate(self, attrs):
        """Validate the education year range.

        Args:
            attrs: Validated education data.

        Returns:
            dict: Validated education data.

        Raises:
            serializers.ValidationError: If the year range is invalid.
        """
        start_year = attrs.get(
            'start_year',
            getattr(self.instance, 'start_year', None)
        )
        end_year = attrs.get(
            'end_year',
            getattr(self.instance, 'end_year', None)
        )

        if end_year and start_year and end_year < start_year:
            raise serializers.ValidationError(
                'End year cannot be earlier than start year.'
            )

        return attrs


class ExperienceSerializer(serializers.ModelSerializer):
    """Serialize and validate a candidate's work experience."""

    class Meta:
        """Define the experience fields exposed through the API."""

        model = Experience

        fields = [
            'id',
            'company_name',
            'job_title',
            'employment_type',
            'location',
            'start_date',
            'end_date',
            'is_current',
            'description',
        ]

        read_only_fields = ['id']

    def validate(self, attrs):
        """Validate the employment date range.

        Args:
            attrs: Validated experience data.

        Returns:
            dict: Validated experience data.

        Raises:
            serializers.ValidationError: If the dates are inconsistent.
        """
        start_date = attrs.get(
            'start_date',
            getattr(self.instance, 'start_date', None)
        )
        end_date = attrs.get(
            'end_date',
            getattr(self.instance, 'end_date', None)
        )
        is_current = attrs.get(
            'is_current',
            getattr(self.instance, 'is_current', False)
        )

        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError(
                'End date cannot be earlier than start date.'
            )

        if is_current and end_date:
            raise serializers.ValidationError(
                'Current employment should not have an end date.'
            )

        return attrs



class CandidateProfileSerializer(serializers.ModelSerializer):
    """Serialize and validate candidate profile information."""

    educations = EducationSerializer(many=True, read_only=True)
    experiences = ExperienceSerializer(many=True, read_only=True)

    resume_name = serializers.SerializerMethodField()

    class Meta:
        """Define the fields exposed by the candidate profile API."""

        model = Candidate

        fields = [
            'candidate_id',
            'full_name',
            'resume_name',
            'skills',
            'location',
            'expected_salary',
            'educations',
            'experiences',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'candidate_id',
            'resume_name',
            'educations',
            'experiences',
            'created_at',
            'updated_at',
        ]

    def get_resume_name(self, obj):
        """Return the stored resume filename without exposing its URL.

        Args:
            obj: Candidate profile instance.

        Returns:
            str or None: Resume filename, if one exists.
        """
        if not obj.resume:
            return None

        return obj.resume.name.rsplit('/', 1)[-1]

    def validate_full_name(self, value):
        """Reject candidate names containing only whitespace.

        Args:
            value: Submitted candidate name.

        Returns:
            str: Normalized candidate name.

        Raises:
            serializers.ValidationError: If the name is empty.
        """
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                'Full name cannot be empty.'
            )

        return value

    def validate_expected_salary(self, value):
        """Ensure the expected salary is positive.

        Args:
            value: Submitted expected salary.

        Returns:
            Decimal: Validated expected salary.

        Raises:
            serializers.ValidationError: If salary is not positive.
        """
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                'Expected salary must be greater than zero.'
            )

        return value


class ResumeUploadSerializer(serializers.Serializer):
    """Validate resume files uploaded by candidates."""

    resume = serializers.FileField()

    MAX_FILE_SIZE = 5 * 1024 * 1024

    MAX_DOCX_ENTRIES = 1000
    MAX_DOCX_UNCOMPRESSED_SIZE = 25 * 1024 * 1024
    MAX_COMPRESSION_RATIO = 100

    ALLOWED_EXTENSIONS = {
        '.pdf',
        '.doc',
        '.docx',
    }

    def validate_resume(self, uploaded_file):
        """Validate the resume's size, extension, and file signature.

        Args:
            uploaded_file: Uploaded resume file.

        Returns:
            UploadedFile: Validated resume file.

        Raises:
            serializers.ValidationError: If the file is invalid.
        """
        extension = Path(uploaded_file.name).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                'Only PDF, DOC, and DOCX files are allowed.'
            )

        if uploaded_file.size == 0:
            raise serializers.ValidationError(
                'Empty files cannot be uploaded.'
            )

        if uploaded_file.size > self.MAX_FILE_SIZE:
            raise serializers.ValidationError(
                'Resume file size cannot exceed 5 MB.'
            )

        uploaded_file.seek(0)
        file_header = uploaded_file.read(1024)
        uploaded_file.seek(0)

        if extension == '.pdf':
            if b'%PDF-' not in file_header:
                raise serializers.ValidationError(
                    'The uploaded file is not a valid PDF.'
                )

        elif extension == '.doc':
            doc_signature = bytes.fromhex(
                'D0 CF 11 E0 A1 B1 1A E1'
            )

            if not file_header.startswith(doc_signature):
                raise serializers.ValidationError(
                    'The uploaded file is not a valid DOC document.'
                )

        elif extension == '.docx':
            try:
                uploaded_file.seek(0)

                with ZipFile(uploaded_file) as archive:
                    file_entries = archive.infolist()

                    # Check the number of files in the archive.
                    if len(file_entries) > self.MAX_DOCX_ENTRIES:
                        raise serializers.ValidationError(
                            'DOCX archive contains too many files.'
                        )

                    # Check the total uncompressed archive size.
                    total_uncompressed_size = sum(
                        entry.file_size
                        for entry in file_entries
                    )

                    if (
                        total_uncompressed_size
                        > self.MAX_DOCX_UNCOMPRESSED_SIZE
                    ):
                        raise serializers.ValidationError(
                            'DOCX archive exceeds the allowed uncompressed size.'
                        )

                    # Check individual file compression ratios.
                    for entry in file_entries:
                        if entry.file_size == 0:
                            continue

                        if entry.compress_size == 0:
                            raise serializers.ValidationError(
                                'DOCX archive contains an invalid compressed entry.'
                            )

                        compression_ratio = (
                            entry.file_size / entry.compress_size
                        )

                        if compression_ratio > self.MAX_COMPRESSION_RATIO:
                            raise serializers.ValidationError(
                                'DOCX archive has an unsafe compression ratio.'
                            )

                    file_names = archive.namelist()

                    # Verify the required Word document components.
                    if (
                        '[Content_Types].xml' not in file_names
                        or 'word/document.xml' not in file_names
                    ):
                        raise serializers.ValidationError(
                            'The uploaded file is not a valid DOCX document.'
                        )

                    # Verify that the archive entries can be read.
                    bad_file = archive.testzip()

                    if bad_file is not None:
                        raise serializers.ValidationError(
                            'DOCX archive contains corrupted data.'
                        )

            except (BadZipFile, OSError, RuntimeError):
                raise serializers.ValidationError(
                    'The uploaded file is not a valid DOCX document.'
                )

            finally:
                uploaded_file.seek(0)
        return uploaded_file
