from django import forms
from ratings.models import Score


# When using ModelForm, form.is_valid() calls Score.clean()
# and insists on validating fields which may not exist at the time!
class ScoreForm(forms.ModelForm):
    def name(self):
        return self.instance.criteria.name
    def min(self):
        return self.instance.criteria.val_min
    def max(self):
        return self.instance.criteria.val_max
    class Meta:
        model = Score
        widgets = {
                'user': forms.HiddenInput(),
                'content_type': forms.HiddenInput(),
                'object_id': forms.HiddenInput(),
                'criteria': forms.HiddenInput(),
                }

