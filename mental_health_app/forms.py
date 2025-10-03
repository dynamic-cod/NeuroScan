from django import forms


class InitialAssessmentForm(forms.Form):
    user_identifier = forms.CharField(max_length=255)
    symptom_text = forms.CharField(widget=forms.Textarea, required=False)


class DetailedAssessmentForm(forms.Form):
    anxiety_score = forms.FloatField(min_value=0, max_value=10)
    depression_score = forms.FloatField(min_value=0, max_value=10)
    stress_score = forms.FloatField(min_value=0, max_value=10)
