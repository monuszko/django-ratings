from django import forms
from ratings.models import Score


class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        widgets = {
                'user': forms.HiddenInput(),
                'content_type': forms.HiddenInput(),
                'object_id': forms.HiddenInput(),
                'criteria': forms.HiddenInput(),
                }

# When using ModelForm, form.is_valid() calls Score.clean()
# and insists on validating fields which don't exist at the time!

#class ScoreForm(forms.Form):
#    value = forms.IntegerField()
#    comment = forms.CharField(max_length=5000)


