from django import forms
from django.core.exceptions import ValidationError
from ratings.models import Choice, Score


class ScoreForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.criteria = kwargs.pop('criteria', None)
        self.obj_id = kwargs.pop('obj_id', None)
        super(ScoreForm, self).__init__(*args, **kwargs)
        self.fields['value'] = forms.ChoiceField(choices=self._get_choices(
            please_select='Please select:'))

    def _get_choices(self, please_select=None):
        choices = Choice.objects.values_list('value', 'label')
        if please_select is not None:
            choices = tuple([(666, please_select)] + list(choices))
        return choices

    def _get_choice_values(self):
        return [first for first, second in self._get_choices()]

    def min(self):
        values = self._get_choice_values()
        return min(values) if values else 0 # min, max fixed in 3.4
    def max(self):
        values = self._get_choice_values()
        return max(values) if values else 0
    def name(self):
        return self.criteria.name

    def clean(self):
        cleaned_data = super(ScoreForm, self).clean()
        value = cleaned_data['value']
        rng = [unicode(v) for v in self._get_choice_values()]
        if Score.objects.filter(user=self.user,
                                object_id=self.obj_id,
                                content_type=self.criteria.content_type,
                                criteria=self.criteria).exists():
            raise ValidationError("Only one score per user allowed.")
        if value not in rng:
            rng = ', '.join(rng)
            raise ValidationError("Values should be in range {0}".format(rng))
        return cleaned_data

    class Meta:
        model = Score
        widgets = {
                'comment': forms.Textarea(attrs={'cols': 40, 'rows': 3}),
                }
