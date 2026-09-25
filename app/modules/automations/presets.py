"""Automations presets."""

from __future__ import annotations

from app.modules.shared.schemas import DashboardModel

WEEKLY_PRESTART_PRESET_ID = "weekly_prestart"


class AutomationPresetResponse(DashboardModel):
    id: str
    name: str
    description: str
    schedule_type: str = "daily"
    default_time: str
    default_timezone: str
    default_days: list[str]
    model: str
    prompt: str


AUTOMATION_PRESETS: dict[str, AutomationPresetResponse] = {
    WEEKLY_PRESTART_PRESET_ID: AutomationPresetResponse(
        id=WEEKLY_PRESTART_PRESET_ID,
        name="Weekly Quota Window Prestart",
        description="Starts and verifies unstarted rolling 7-day secondary quota windows for idle accounts.",
        schedule_type="daily",
        default_time="00:00",
        default_timezone="UTC",
        default_days=["mon"],
        model="gpt-5.3-codex-spark",
        prompt="Prestart weekly quota window.",
    )
}


def list_automation_presets() -> list[AutomationPresetResponse]:
    return list(AUTOMATION_PRESETS.values())


def get_automation_preset(preset_id: str) -> AutomationPresetResponse | None:
    return AUTOMATION_PRESETS.get(preset_id)
