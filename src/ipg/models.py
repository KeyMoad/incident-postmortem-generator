from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


IncidentStatus = Literal["resolved", "mitigated", "ongoing"]
Severity = Literal["SEV-1", "SEV-2", "SEV-3", "SEV-4"]
Environment = Literal["production", "staging", "dev"]
ServiceTier = Literal["critical", "high", "medium", "low"]

DetectionSource = Literal["monitoring_alert", "customer_report", "internal_report", "partner"]

TimelineType = Literal[
    "trigger",
    "detection",
    "investigation",
    "mitigation",
    "recovery",
    "comms",
    "followup",
]

Priority = Literal["P0", "P1", "P2", "P3"]
ActionType = Literal["prevention", "detection", "response", "reliability", "process", "documentation"]
ActionStatus = Literal["open", "in_progress", "done"]


class Link(BaseModel):
    label: str = Field(min_length=1)
    url: HttpUrl

    model_config = {"extra": "forbid"}


class Service(BaseModel):
    name: str = Field(min_length=1)
    owner_team: str = Field(min_length=1)
    environment: Environment
    tier: ServiceTier

    model_config = {"extra": "forbid"}


class TimeWindow(BaseModel):
    timezone: str = Field(default="UTC", min_length=1)

    start: datetime
    end: datetime
    detected: datetime
    mitigated: datetime

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_times(self) -> "TimeWindow":
        if self.start >= self.end:
            raise ValueError("time.start must be before time.end")

        if not (self.start <= self.detected <= self.end):
            raise ValueError("time.detected must be within [start, end]")

        if not (self.start <= self.mitigated <= self.end):
            raise ValueError("time.mitigated must be within [start, end]")

        if self.mitigated < self.detected:
            raise ValueError("time.mitigated must be >= time.detected")

        return self


class Summary(BaseModel):
    what_happened: str = Field(min_length=1)
    user_impact: str = Field(min_length=1)
    duration_minutes: int = Field(ge=0)

    model_config = {"extra": "forbid"}


class SlaSlo(BaseModel):
    slo_breached: bool
    slo_name: Optional[str] = None
    breach_window: Optional[str] = None

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_breach_fields(self) -> "SlaSlo":
        if self.slo_breached and (not self.slo_name or not self.breach_window):
            raise ValueError("impact.sla_slo.slo_name and breach_window are required when slo_breached=true")
        return self


class Impact(BaseModel):
    customers_affected_estimate: int = Field(ge=0)
    regions_affected: List[str] = Field(default_factory=list)

    request_error_rate_peak_percent: float = Field(ge=0)
    latency_p95_peak_ms: int = Field(ge=0)

    business_impact: str = Field(min_length=1)
    sla_slo: SlaSlo

    model_config = {"extra": "forbid"}


class Signal(BaseModel):
    source: str = Field(min_length=1)
    name: str = Field(min_length=1)
    details: str = Field(min_length=1)

    model_config = {"extra": "forbid"}


class CustomerReports(BaseModel):
    count: int = Field(ge=0)
    channels: List[str] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class Detection(BaseModel):
    detected_by: DetectionSource
    signals: List[Signal] = Field(default_factory=list)
    customer_reports: CustomerReports
    gaps: List[str] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class TimelineEvent(BaseModel):
    time: datetime
    type: TimelineType
    actor: str = Field(min_length=1)
    message: str = Field(min_length=1)
    links: List[Link] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class RootCause(BaseModel):
    direct_cause: str = Field(min_length=1)
    contributing_factors: List[str] = Field(default_factory=list)
    why_it_was_not_prevented: str = Field(min_length=1)

    model_config = {"extra": "forbid"}


class Response(BaseModel):
    what_worked_well: List[str] = Field(default_factory=list)
    what_did_not_work_well: List[str] = Field(default_factory=list)
    where_we_got_lucky: List[str] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class InternalComms(BaseModel):
    channel: str = Field(min_length=1)
    started_at: datetime

    model_config = {"extra": "forbid"}


class ExternalComms(BaseModel):
    status_page_used: bool
    first_update_at: Optional[datetime] = None
    updates_count: int = Field(default=0, ge=0)
    customer_message: Optional[str] = None

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_external(self) -> "ExternalComms":
        if self.status_page_used and self.first_update_at is None:
            raise ValueError("communication.external.first_update_at is required when status_page_used=true")
        return self


class Communication(BaseModel):
    internal: InternalComms
    external: ExternalComms

    model_config = {"extra": "forbid"}


class ActionItem(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    owner: str = Field(min_length=1)

    priority: Priority
    due: date

    type: ActionType
    status: ActionStatus

    success_criteria: Optional[str] = None
    links: List[Link] = Field(default_factory=list)

    model_config = {"extra": "forbid"}

    @field_validator("id")
    @classmethod
    def validate_action_id(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("action_items[].id is too short")
        return v


class ReferenceList(BaseModel):
    dashboards: List[Link] = Field(default_factory=list)
    logs: List[Link] = Field(default_factory=list)
    runbooks: List[Link] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class Incident(BaseModel):
    version: str = Field(default="1.0")
    incident_id: str = Field(min_length=1)

    title: str = Field(min_length=1)
    status: IncidentStatus
    severity: Severity

    service: Service
    time: TimeWindow
    summary: Summary
    impact: Impact
    detection: Detection
    timeline: List[TimelineEvent] = Field(default_factory=list)

    root_cause: RootCause
    response: Response
    communication: Communication

    action_items: List[ActionItem] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    references: ReferenceList = Field(default_factory=ReferenceList)

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_timeline_order(self) -> "Incident":
        if self.timeline:
            times = [e.time for e in self.timeline]
            if any(t2 < t1 for t1, t2 in zip(times, times[1:])):
                raise ValueError("timeline events must be sorted by time (ascending)")
        return self
