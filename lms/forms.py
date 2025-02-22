from django import forms
from datetime import date

class LeaveApplicationForm(forms.Form):
    LEAVE_TYPES = [
        ('', 'Select Leave Type'),
        ('casual', 'Casual Leave'),
        ('medical', 'Medical Leave'),
        ('privilege', 'Privilege Leave'),
    ]

    DURATION = [
        ('', 'Select Duration'),
        ('single', 'Single Day'),
        ('multiple', 'Multiple Days'),
    ]

    leave_type = forms.ChoiceField(choices=LEAVE_TYPES, widget=forms.Select)
    duration = forms.ChoiceField(choices=DURATION, widget=forms.Select, required=False)
    reason = forms.CharField(widget=forms.Textarea, required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    proof = forms.FileField(required=False)
    print("form")

    def clean(self):
        cleaned_data = super().clean()
        leave_type = cleaned_data.get("leave_type")
        duration = cleaned_data.get("duration")
        date_field = cleaned_data.get("date")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        proof = cleaned_data.get("proof")
        reason = cleaned_data.get("reason")
        print("cleaned data")

        # Validate leave duration
        total_leave_days = 0
        if duration == "single" and date_field:
            total_leave_days = 1
        elif duration == "multiple" and start_date and end_date:
            total_leave_days = (end_date - start_date).days + 1
        print("total leave")

        # Restrict past dates
        today = date.today()
        if date_field and date_field < today:
            self.add_error("date", "Selected date cannot be in the past.")
        if start_date and start_date < today:
            self.add_error("start_date", "Start date cannot be in the past.")
        if end_date and end_date < today:
            self.add_error("end_date", "End date cannot be in the past.")
        print("date check")

        # Reason minimum character length
        if len(reason) < 5:
            self.add_error("reason", "Reason must be at least 5 characters long.")

        if duration == "multiple" and  start_date >= end_date:
            self.add_error("end_date", "End date cannot be earlier than the start date.")

        # Validate file type for proof
        if proof:
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
            if proof.content_type not in allowed_types:
                self.add_error("proof", "Only PDF, JPG, or PNG files are allowed.")

        # Validation based on leave type
        if leave_type == "casual":
            if duration == "single" and not date_field:
                self.add_error("date", "Date is required for single-day casual leave.")
            if duration == "multiple" and (not start_date or not end_date):
                self.add_error("start_date", "Start date is required for multiple-day casual leave.")
                self.add_error("end_date", "End date is required for multiple-day casual leave.")
        elif leave_type == "medical":
            if not start_date or not end_date:
                self.add_error("start_date", "Start date is required for medical leave.")
                self.add_error("end_date", "End date is required for medical leave.")
            if not proof:
                self.add_error("proof", "Proof is required for medical leave.")
        elif leave_type == "privilege":
            if duration == "single" and not date_field:
                self.add_error("date", "Date is required for single-day privilege leave.")
            if duration == "multiple" and (not start_date or not end_date):
                self.add_error("start_date", "Start date is required for multiple-day privilege leave.")
                self.add_error("end_date", "End date is required for multiple-day privilege leave.")
            if not proof:
                self.add_error("proof", "Proof is required for privilege leave.")

        # Cross-check start and end dates
        if start_date and end_date and start_date > end_date:
            self.add_error("end_date", "End date cannot be before start date.")
