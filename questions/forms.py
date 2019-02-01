from django import forms as django_forms


class AnswerForm(django_forms.Form):
    text = django_forms.CharField(widget=django_forms.Textarea, required=True)


class AskForm(django_forms.Form):
    title = django_forms.CharField(widget=django_forms.TextInput(
        attrs={'class': 'form-control',
               'type': 'text',
               'id': 'id_title',
               'placeholder': ''}
    ), required=True)

    text = django_forms.CharField(widget=django_forms.Textarea(
        attrs={'class': 'form-control',
               'type': 'text',
               'id': 'id_text',
               'placeholder': ''}
    ), required=True)

    tag = django_forms.CharField(widget=django_forms.TextInput(
        attrs={'class': 'form-control',
               'type': 'text',
               'id': 'tags',
               'placeholder': 'tags'}
    ), required=False)
