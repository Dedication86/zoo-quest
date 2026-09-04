"""
Challenge type registry.

Each challenge type declares what its `config` JSON must contain and how the
admin should label things. Verification logic (M3) lives next to this in
`verifiers.py`; keeping the config contract here means the admin form, the
fixture loader and the verifier all agree on one definition.

Adding a type later = add an entry here + a verifier + a frontend component.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChallengeType:
    key: str
    label: str
    description: str
    needs_markers: bool = False  # completed by scanning one of accept_markers
    needs_options: bool = False  # multiple choice with a correct answer
    any_answer: bool = False  # observation: any choice completes it
    self_report: bool = False  # photo: "Done" completes it
    config_keys: tuple = field(default_factory=tuple)

    def validate_config(self, config: dict, accept_marker_count: int) -> list[str]:
        """Return a list of human-readable problems. Empty list = valid."""
        problems = []
        config = config or {}
        if self.needs_markers and accept_marker_count == 0:
            problems.append(
                "This challenge type is completed by scanning, so pick at least one accepted marker."
            )
        if self.needs_options or self.any_answer:
            options = config.get("options")
            if not isinstance(options, list) or len(options) < 2:
                problems.append("config.options must be a list of at least two answer choices.")
            elif any(not isinstance(o, str) or not o.strip() for o in options):
                problems.append("Every option must be non-empty text.")
        if self.needs_options:
            correct = config.get("correct")
            if not correct:
                problems.append("config.correct is required for this challenge type.")
            elif isinstance(config.get("options"), list) and correct not in config["options"]:
                problems.append("config.correct must exactly match one of the options.")
        if self.any_answer:
            timer = config.get("timer_seconds", 30)
            if not isinstance(timer, int) or timer < 5 or timer > 300:
                problems.append("config.timer_seconds must be a whole number between 5 and 300.")
        return problems


CHALLENGE_TYPES: dict[str, ChallengeType] = {
    t.key: t
    for t in [
        ChallengeType(
            key="animal_hunt",
            label="Animal Hunt",
            description="Find a specific animal and scan the marker at its exhibit.",
            needs_markers=True,
        ),
        ChallengeType(
            key="scavenger",
            label="Scavenger Hunt",
            description="A clue instead of a name. Any accepted marker completes it.",
            needs_markers=True,
        ),
        ChallengeType(
            key="who_am_i",
            label="Who Am I?",
            description="A riddle with multiple-choice answers.",
            needs_options=True,
            config_keys=("options", "correct"),
        ),
        ChallengeType(
            key="observation",
            label="Observation",
            description="Watch for a timer, then answer. Any answer counts; the point is watching.",
            any_answer=True,
            config_keys=("timer_seconds", "options"),
        ),
        ChallengeType(
            key="photo",
            label="Photo",
            description="Take a photo (kept on the family's phone) and tap Done.",
            self_report=True,
        ),
        ChallengeType(
            key="conservation",
            label="Conservation",
            description="A question with a real takeaway. Multiple choice with an explanation.",
            needs_options=True,
            config_keys=("options", "correct"),
        ),
    ]
}

CHALLENGE_TYPE_CHOICES = [(t.key, t.label) for t in CHALLENGE_TYPES.values()]


def get_type(key: str) -> ChallengeType:
    return CHALLENGE_TYPES[key]
