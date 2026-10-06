from django import forms

from ..services import CipherService


class CipherOperationForm(forms.Form):
    algorithm = forms.ChoiceField(choices=[(key, value) for key, value in CipherService.ALGORITHMS.items()])
    operation = forms.ChoiceField(choices=(("encrypt", "تشفير"), ("decrypt", "فك التشفير")))
    text = forms.CharField(widget=forms.Textarea, max_length=100_000, strip=False)
    key = forms.CharField(required=False, max_length=16_384, strip=False)
    parameter = forms.CharField(required=False, max_length=64)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("algorithm") in {"des", "rsa", "dsa", "vigenere", "playfair", "hill", "vernam"} and not cleaned.get("key"):
            self.add_error("key", "هذا الاختيار يحتاج مفتاحاً")
        return cleaned