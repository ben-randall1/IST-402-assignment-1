"""Reviewed, fixed coursework content. No generated therapeutic instructions."""
SKILL = {
    "skill_id": "breathing-4-6", "version": 1, "title": "Paced breathing",
    "cycles": 6, "inhale_seconds": 4, "exhale_seconds": 6, "planned_ms": 60000,
    "instructions": "Breathe in for four counts, then out for six. Repeat six times, only if comfortable. You can stop at any point.",
}
RESPONSES = {
    "offer_choice": "You can choose a short practice, or leave it here. You don't need to describe anything.",
    "explain_breathing": "This practice uses four counts in and six counts out, for six rounds. The screen carries the pace. You can stop at any point.",
    "usual_available": "The skill you chose as your usual is available. You can use it or choose something else.",
    "different_choice": "You can return to the available choices. Nothing starts until you choose Start.",
    "outside_scope": "This coursework prototype can't answer that request. You can view the fixed skill, leave, or open crisis-support information.",
}
CRISIS_COPY = "Crisis-support information is available here. This coursework prototype is not monitored and cannot contact services for you. You may open the information, leave, or choose another screen."
# Conservative substring matching: quotes/negation may match; euphemisms/languages may be missed.
CRISIS_PHRASES = ("kill myself", "hurt myself", "harm myself", "end my life", "suicide", "suicidal", "self-harm", "self harm")


def crisis_match(text: str) -> bool:
    return any(phrase in text.casefold() for phrase in CRISIS_PHRASES)
