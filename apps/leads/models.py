"""Lead models: every form submission is stored before it is emailed."""

from __future__ import annotations

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import OrderableModel, TimeStampedModel


class LeadStatus(models.TextChoices):
    """Sales pipeline stages."""

    NEW = "new", "New"
    CONTACTED = "contacted", "Contacted"
    QUOTED = "quoted", "Quoted"
    WON = "won", "Won"
    LOST = "lost", "Lost"


class ChoiceGroup(models.TextChoices):
    """Lookup groups an admin can extend without a migration."""

    ENQUIRY_TYPE = "enquiry_type", ""
    EMERGENCY_ISSUE = "emergency_issue", "Emergency"
    BUILDING_TYPE = "building_type", "Quote wizard: building type"
    FLOOR_AREA = "floor_area", "Quote wizard: floor area band"
    SYSTEM_TYPE = "system_type", "Quote wizard: system type"
    TIMELINE = "timeline", "Quote wizard: timeline"
    BUDGET_BAND = "budget_band", "Quote wizard: budget band"


class FormFieldChoice(OrderableModel, TimeStampedModel):
    """An option in a form dropdown, editable by admins (e.g. add a new building type)."""

    group = models.CharField(
        max_length=20,
        choices=ChoiceGroup.choices,
        db_index=True,
        help_text="Which form field this option belongs to.",
    )
    label = models.CharField(max_length=80, help_text="What the visitor sees.")
    value = models.SlugField(
        max_length=60,
        help_text="Short internal code, e.g. 'restaurant'. Letters, numbers and hyphens.",
    )
    is_active = models.BooleanField(default=True, help_text="Untick to hide from the form.")

    class Meta(OrderableModel.Meta):
        ordering = ["group", "order", "label"]
        verbose_name = "Form dropdown option"
        verbose_name_plural = "Form dropdown options"
        constraints = [
            models.UniqueConstraint(fields=["group", "value"], name="unique_choice_per_group")
        ]

    def __str__(self) -> str:
        return f"{self.get_group_display()} → {self.label}"


class LeadNote(TimeStampedModel):
    """An internal note attached to any lead type."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    lead = GenericForeignKey("content_type", "object_id")
    author = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.SET_NULL, editable=False
    )
    note = models.TextField(help_text="Internal only — never shown to the customer.")

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["content_type", "object_id"])]
        verbose_name = "Internal note"
        verbose_name_plural = "Internal notes"

    def __str__(self) -> str:
        return self.note[:60]


class LeadBase(TimeStampedModel):
    """Fields and behaviour shared by every kind of lead."""

    status = models.CharField(
        max_length=12,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW,
        db_index=True,
        help_text="Move the lead through the pipeline as you work it.",
    )
    name = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    source_url = models.CharField(
        max_length=300, blank=True, editable=False, help_text="Page the form was sent from."
    )
    referrer = models.CharField(max_length=300, blank=True, editable=False)
    user_agent = models.CharField(max_length=300, blank=True, editable=False)
    consent = models.BooleanField(
        default=False,
        help_text="Visitor agreed to be contacted about their enquiry.",
    )
    notified_at = models.DateTimeField(
        null=True, blank=True, editable=False, help_text="When the notification email was sent."
    )
    notes = GenericRelation(LeadNote)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    @property
    def display_name(self) -> str:
        """Name or phone for list views.

        Returns:
            ``name`` if given, else the phone number.
        """
        return self.name or self.phone

    def notification_subject(self) -> str:
        """Subject line for the notification email.

        Returns:
            Human-readable subject.
        """
        return f"New website lead from {self.display_name}"


class ContactEnquiry(LeadBase):
    """A general enquiry from the contact page (Path B: contract buyers)."""

    company = models.CharField(max_length=120, blank=True)
    enquiry_type = models.ForeignKey(
        FormFieldChoice,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"group": ChoiceGroup.ENQUIRY_TYPE},
        related_name="+",
    )
    message = models.TextField()
    

    class Meta(LeadBase.Meta):
        verbose_name = "Contact enquiry"
        verbose_name_plural = "Contact enquiries"

    def __str__(self) -> str:
        return f"Enquiry from {self.display_name}"

    def notification_subject(self) -> str:
        """Subject line including the enquiry type.

        Returns:
            Subject string.
        """
        kind = self.enquiry_type.label if self.enquiry_type else "General"
        return f"[{kind}] Website enquiry from {self.display_name}"

class RequestEnquiry(LeadBase):
    """A general enquiry from the contact page (Path B: contract buyers)."""

    company = models.CharField(max_length=120, blank=True)
    enquiry_type = models.ForeignKey(
        FormFieldChoice,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"group": ChoiceGroup.ENQUIRY_TYPE},
        related_name="+",
    )
    message = models.TextField()
    postcode = models.CharField(max_length=15)

    class Meta(LeadBase.Meta):
        verbose_name = "Request enquiry"
        verbose_name_plural = "Request enquiries"

    def __str__(self) -> str:
        return f"Enquiry from {self.display_name}"

    def notification_subject(self) -> str:
        """Subject line including the enquiry type.

        Returns:
            Subject string.
        """
        kind = self.enquiry_type.label if self.enquiry_type else "General"
        return f"[{kind}] Website enquiry from {self.display_name}"

class EmergencyCallout(LeadBase):
    """A one-field callback request from the emergency page (Path A)."""
    name = models.CharField(max_length=50, blank=False)
    postcode = models.CharField(max_length=12, blank=True)
    issue = models.ForeignKey(
        FormFieldChoice,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"group": ChoiceGroup.EMERGENCY_ISSUE},
        related_name="+",
    )
    details = models.CharField(max_length=300, blank=True)
    called_back_at = models.DateTimeField(
        null=True, blank=True, help_text="Record when an engineer rang the customer back."
    )

    class Meta(LeadBase.Meta):
        verbose_name = _("Emergency callback")
        verbose_name_plural = _("Emergency callbacks")

    def __str__(self) -> str:
        return f"EMERGENCY {self.phone}"

    def notification_subject(self) -> str:
        """Urgent subject line.

        Returns:
            Subject string prefixed for filtering.
        """
        where = f" ({self.postcode})" if self.postcode else ""
        return f"🚨 EMERGENCY callback: {self.phone}{where}"
