"""
Content: everything a zoo authors. Read constantly by families, edited rarely
by staff. See Blueprint, Section D.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from apps.tenants.models import ZooScopedModel

from .challenge_types import CHALLENGE_TYPE_CHOICES, get_type


class IUCNStatus(models.TextChoices):
    LC = "LC", "Least Concern"
    NT = "NT", "Near Threatened"
    VU = "VU", "Vulnerable"
    EN = "EN", "Endangered"
    CR = "CR", "Critically Endangered"
    EW = "EW", "Extinct in the Wild"
    EX = "EX", "Extinct"
    DD = "DD", "Data Deficient"


class Difficulty(models.TextChoices):
    EASY = "easy", "Easy"
    MEDIUM = "medium", "Medium"
    HARD = "hard", "Hard"


class Exhibit(ZooScopedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="exhibits/", blank=True)
    map_x = models.DecimalField(
        max_digits=5, decimal_places=2, default=50, help_text="Pin position, % from the left of the map image"
    )
    map_y = models.DecimalField(
        max_digits=5, decimal_places=2, default=50, help_text="Pin position, % from the top of the map image"
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("zoo", "slug")]
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Animal(ZooScopedModel):
    exhibit = models.ForeignKey(Exhibit, on_delete=models.PROTECT, related_name="animals")
    name = models.CharField(max_length=120, help_text="What a kid calls it: Giraffe")
    slug = models.SlugField()
    species = models.CharField(max_length=160, blank=True, help_text="Reticulated giraffe")
    scientific_name = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="animals/", blank=True)
    emoji = models.CharField(max_length=8, blank=True, help_text="Fallback icon when there is no image")
    fun_facts = models.JSONField(
        default=list, blank=True, help_text="List of short facts, one per line in the admin"
    )
    conservation_status = models.CharField(max_length=2, choices=IUCNStatus.choices, default=IUCNStatus.DD)
    conservation_info = models.TextField(blank=True, help_text="Written for a nine-year-old")
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Lowercase tags badges and clues key off: africa, reptile, stripes",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("zoo", "slug")]
        ordering = ["exhibit__sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Marker(ZooScopedModel):
    """One physical QR code. Its URL is /s/<code>."""

    code = models.CharField(
        max_length=40, blank=True, help_text="Printed on the sign. Generated if left blank."
    )
    exhibit = models.ForeignKey(Exhibit, on_delete=models.PROTECT, related_name="markers")
    animal = models.ForeignKey(
        Animal, on_delete=models.SET_NULL, null=True, blank=True, related_name="markers"
    )
    label = models.CharField(max_length=120, help_text="For staff: 'Giraffe viewing rail'")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("zoo", "code")]
        ordering = ["exhibit__sort_order", "code"]

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def generate_code(self):
        prefix = "".join(w[0] for w in self.zoo.name.split() if w[:1].isalpha())[:4].upper() or "ZOO"
        subject = (self.animal.slug if self.animal else self.exhibit.slug).replace("-", "").upper()[:14]
        n = Marker.objects.filter(zoo=self.zoo, code__startswith=f"{prefix}-{subject}-").count() + 1
        return f"{prefix}-{subject}-{n:03d}"

    @property
    def scan_path(self):
        return f"/s/{self.code}"


class Challenge(ZooScopedModel):
    title = models.CharField(max_length=120)
    slug = models.SlugField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPE_CHOICES)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)
    xp_reward = models.PositiveIntegerField(
        help_text="Leave 0 to use the zoo default for this difficulty", default=0
    )
    prompt = models.TextField(help_text="What the family reads")
    hint = models.TextField(blank=True)
    explanation = models.TextField(blank=True, help_text="Shown after completion: the learning beat")
    animal = models.ForeignKey(
        Animal, on_delete=models.SET_NULL, null=True, blank=True, related_name="challenges"
    )
    exhibit = models.ForeignKey(
        Exhibit, on_delete=models.SET_NULL, null=True, blank=True, related_name="challenges"
    )
    accept_markers = models.ManyToManyField(
        Marker,
        blank=True,
        related_name="challenges",
        help_text="Scanning any of these completes the challenge",
    )
    config = models.JSONField(
        default=dict, blank=True, help_text="Type-specific: options, correct, timer_seconds"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("zoo", "slug")]
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.get_challenge_type_display()})"

    @property
    def type_def(self):
        return get_type(self.challenge_type)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.xp_reward:
            self.xp_reward = self.zoo.xp_for_difficulty(self.difficulty)
        super().save(*args, **kwargs)

    def validate_config(self, accept_marker_count=None):
        if accept_marker_count is None:
            accept_marker_count = self.accept_markers.count() if self.pk else 0
        return self.type_def.validate_config(self.config, accept_marker_count)

    def clean(self):
        # Marker-based validation runs in the admin form, where the M2M selection is known.
        problems = [p for p in self.validate_config(accept_marker_count=1) if "marker" not in p]
        if problems:
            raise ValidationError({"config": problems})

    def public_config(self):
        """Config safe to send to the browser. Never includes the correct answer."""
        return {k: v for k, v in (self.config or {}).items() if k != "correct"}


class Badge(ZooScopedModel):
    class Rule(models.TextChoices):
        SCAN_COUNT = "scan_count", "Scan N markers"
        DISCOVER_ANIMAL = "discover_animal", "Discover specific animal(s)"
        DISCOVER_COUNT = "discover_count", "Discover N animals (optionally with a tag)"
        EXHIBIT_COUNT = "exhibit_count", "Scan in N different exhibits"
        CHALLENGE_TYPE_COUNT = "challenge_type_count", "Complete N challenges of a type"
        QUEST_COMPLETE = "quest_complete", "Complete a quest"

    name = models.CharField(max_length=80)
    slug = models.SlugField()
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=8, blank=True, help_text="Emoji, used when there is no image")
    image = models.ImageField(upload_to="badges/", blank=True)
    rule_type = models.CharField(max_length=30, choices=Rule.choices)
    rule_config = models.JSONField(
        default=dict,
        blank=True,
        help_text='e.g. {"count": 5, "tag": "africa"} or {"quest_slug": "savanna-safari"}',
    )
    xp_reward = models.PositiveIntegerField(default=0)
    is_secret = models.BooleanField(default=False, help_text="Hidden in the badge case until earned")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [("zoo", "slug")]
        ordering = ["name"]

    def __str__(self):
        return f"{self.icon} {self.name}".strip()

    def rule_sentence(self):
        c = self.rule_config or {}
        match self.rule_type:
            case self.Rule.SCAN_COUNT:
                return f"Scan {c.get('count', '?')} marker(s)"
            case self.Rule.DISCOVER_ANIMAL:
                return "Discover " + (", ".join(c.get("animal_slugs", [])) or "a specific animal")
            case self.Rule.DISCOVER_COUNT:
                tag = f" tagged '{c['tag']}'" if c.get("tag") else ""
                return f"Discover {c.get('count', '?')} animal(s){tag}"
            case self.Rule.EXHIBIT_COUNT:
                return f"Scan a marker in {c.get('count', '?')} different exhibits"
            case self.Rule.CHALLENGE_TYPE_COUNT:
                return f"Complete {c.get('count', '?')} {c.get('challenge_type', '?')} challenge(s)"
            case self.Rule.QUEST_COMPLETE:
                return f"Complete quest '{c.get('quest_slug', '?')}'"
        return ""


class Quest(ZooScopedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="quests/", blank=True)
    xp_reward = models.PositiveIntegerField(default=0, help_text="Leave 0 to use the zoo default")
    badge = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True, related_name="quests")
    estimated_minutes = models.PositiveIntegerField(null=True, blank=True)
    starts_at = models.DateTimeField(null=True, blank=True, help_text="For seasonal quests. Blank = always")
    ends_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    challenges = models.ManyToManyField(Challenge, through="QuestChallenge", related_name="quests")

    class Meta:
        unique_together = [("zoo", "slug")]
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.xp_reward:
            self.xp_reward = int(self.zoo.setting("quest_complete_xp", 0))
        super().save(*args, **kwargs)

    def ordered_steps(self):
        return self.steps.select_related("challenge", "challenge__animal", "challenge__exhibit").order_by(
            "order"
        )


class QuestChallenge(models.Model):
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="steps")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="quest_steps")
    order = models.PositiveIntegerField()
    is_final = models.BooleanField(
        default=False, help_text="The last mission; completing it completes the quest"
    )

    class Meta:
        unique_together = [("quest", "order"), ("quest", "challenge")]
        ordering = ["order"]

    def __str__(self):
        return f"{self.quest} #{self.order}: {self.challenge.title}"


class Level(ZooScopedModel):
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=80)
    xp_required = models.PositiveIntegerField()

    class Meta:
        unique_together = [("zoo", "number")]
        ordering = ["number"]

    def __str__(self):
        return f"{self.number}. {self.title} ({self.xp_required} XP)"

    @classmethod
    def for_xp(cls, zoo, xp):
        """Current level and the next threshold for a given XP total."""
        levels = list(cls.objects.filter(zoo=zoo).order_by("number"))
        current = None
        nxt = None
        for lvl in levels:
            if xp >= lvl.xp_required:
                current = lvl
            elif nxt is None:
                nxt = lvl
        return current, nxt
