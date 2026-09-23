"""Public lead forms with plain-English validation and a honeypot."""

from __future__ import annotations

import re
from typing import Any

from django import forms
from django.core.exceptions import ValidationError

from .models import ChoiceGroup, ContactEnquiry, EmergencyCallout, FormFieldChoice, RequestEnquiry

UK_PHONE_DIGITS = re.compile(r"\d")
MIN_PHONE_DIGITS = 10
HONEYPOT_FIELD = "website_url"


def validate_phone(value: str) -> str:
    """Accept any plausible UK or international phone number.

    Args:
        value: Raw phone input.

    Returns:
        The stripped value.

    Raises:
        ValidationError: If fewer than ten digits are present.
    """
    digits = "".join(UK_PHONE_DIGITS.findall(value))
    if len(digits) < MIN_PHONE_DIGITS:
        raise ValidationError("Please enter a full phone number including the area code.")
    return value.strip()


class HoneypotMixin(forms.Form):
    """Adds an invisible field that bots fill in and humans never see."""

    website_url = forms.CharField(
        required=False,
        label="Leave this field empty",
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )

    def clean_website_url(self) -> str:
        """Reject submissions where the honeypot has been filled.

        Returns:
            Always ``''`` for genuine submissions.

        Raises:
            ValidationError: If a bot filled the field.
        """
        if self.cleaned_data.get(HONEYPOT_FIELD):
            raise ValidationError("Submission rejected.")
        return ""


class ChoiceQuerysetMixin:
    """Populates lookup-table dropdowns from ``FormFieldChoice``."""

    @staticmethod
    def choices_for(group: str) -> Any:
        """Active options for a dropdown group.

        Args:
            group: A ``ChoiceGroup`` value.

        Returns:
            Ordered queryset.
        """
        return FormFieldChoice.objects.filter(group=group, is_active=True)


class ContactEnquiryForm(HoneypotMixin, ChoiceQuerysetMixin, forms.ModelForm):
    """Contact page form for contract buyers and general enquiries."""

    class Meta:
        model = ContactEnquiry
        fields = ["name", "company", "phone", "email", "enquiry_type", "message", "consent"]
        labels = {
            "name": "Your name",
            "company": "Company or site (optional)",
            "phone": "Phone number",
            "email": "Email address",
            "enquiry_type": "What is this about?",
            "message": "Tell us about the site and equipment",
            "consent": "I'm happy for MehrCool to contact me about this enquiry.",
        }
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["email"].required = True
        self.fields["consent"].required = True
        self.fields["enquiry_type"].queryset = self.choices_for(ChoiceGroup.ENQUIRY_TYPE)
        self.fields["enquiry_type"].empty_label = "Choose one…"
        self.fields["phone"].widget.attrs.update(
            {"type": "tel", "autocomplete": "tel", "inputmode": "tel"}
        )
        self.fields["email"].widget.attrs.update({"autocomplete": "email"})
        self.fields["name"].widget.attrs.update({"autocomplete": "name"})
        self.fields["company"].widget.attrs.update({"autocomplete": "organization"})

    def clean_phone(self) -> str:
        """Validate the phone number."""
        return validate_phone(self.cleaned_data["phone"])


class RequestEnquiryForm(HoneypotMixin, ChoiceQuerysetMixin, forms.ModelForm):
    """Contact page form for contract buyers and general enquiries."""

    class Meta:
        model = RequestEnquiry
        fields = ["name", "company", "phone", "email", "postcode", "enquiry_type", "message", "consent"]
        labels = {
            "name": "Your name",
            "company": "Company or site (optional)",
            "phone": "Phone number",
            "email": "Email address",
            "postcode": "The site post code",
            "enquiry_type": "What is this about?",
            "message": "Tell us about the site and equipment",
            "consent": "I'm happy for MehrCool to contact me about this enquiry.",
        }
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["email"].required = True
        self.fields["consent"].required = True
        self.fields["enquiry_type"].required = True
        self.fields["enquiry_type"].queryset = self.choices_for(ChoiceGroup.ENQUIRY_TYPE)
        self.fields["enquiry_type"].empty_label = "Choose one…"
        self.fields["phone"].widget.attrs.update(
            {"type": "tel", "autocomplete": "tel", "inputmode": "tel"}
        )
        self.fields["email"].widget.attrs.update({"autocomplete": "email"})
        self.fields["postcode"].widget.attrs.update({"autocomplete": "post code"})
        self.fields["name"].widget.attrs.update({"autocomplete": "name"})
        self.fields["company"].widget.attrs.update({"autocomplete": "organization"})

    def clean_phone(self) -> str:
        """Validate the phone number."""
        return validate_phone(self.cleaned_data["phone"])


class EmergencyCalloutForm(HoneypotMixin, ChoiceQuerysetMixin, forms.ModelForm):
    """One-field callback form: phone is the only required input."""

    class Meta:
        model = EmergencyCallout
        fields = ["name","phone", "postcode", "issue", "details"]
        labels = {
            "name": "Your name",
            "phone": "Your mobile number",
            "postcode": "Site postcode (optional)",
            "issue": "What has failed? (optional)",
            "details": "Anything else (optional)",
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["issue"].queryset = self.choices_for(ChoiceGroup.EMERGENCY_ISSUE)
        self.fields["issue"].empty_label = "Choose if you know…"
        self.fields["phone"].widget.attrs.update(
            {
                "type": "tel",
                "autocomplete": "tel",
                "inputmode": "tel",
                "placeholder": "07… or +44…",
                "autofocus": "autofocus",
            }
        )
        self.fields["postcode"].widget.attrs.update(
            {"autocomplete": "postal-code", "placeholder": "e.g. E14 9FP"}
        )

    def clean_phone(self) -> str:
        """Validate the phone number."""
        return validate_phone(self.cleaned_data["phone"])
