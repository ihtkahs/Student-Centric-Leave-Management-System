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

    def clean(self):
        cleaned_data = super().clean()
        leave_type = cleaned_data.get("leave_type")
        duration = cleaned_data.get("duration")
        date_field = cleaned_data.get("date")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        proof = cleaned_data.get("proof")

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
