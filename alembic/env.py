from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.database.base import Base
from app.models.user import User
from app.models.student import Student
from app.models.goal import Goal
from app.models.roadmap import Roadmap
from app.models.milestone import Milestone
from app.models.task import Task
from app.models.passport import CareerPassport
from app.models.achievement import Achievement
from app.models.project import Project
from app.models.certificate import Certificate
from app.models.career_category import CareerCategory
from app.models.career import Career
from app.models.career_skill import CareerSkill, CareerSubject
from app.models.university import University
from app.models.university_course import UniversityCourse
from app.models.weekly_checkin import WeeklyCheckin
from app.models.notification import Notification
from app.models.roadmap_year_plan import RoadmapYearPlan
from app.models.roadmap_monthly_plan import MonthlyPlan
from app.models.roadmap_weekly_plan import WeeklyPlan, WeeklyPlanItem
from app.models.organization import Organization, OrganizationMembership
from app.models.parent import Parent, ParentStudent, ParentStudentInvitation
from app.models.audit import AuditLog
from app.models.organization_onboarding import OrganizationOnboarding
from app.models.organization_settings import OrganizationSettings
from app.models.counselor_assignment import CounselorProfile, CounselorStudentAssignment
from app.models.counselor_note import CounselorNote
from app.models.student_import import StudentImportJob
from app.models.organization_report import OrganizationReportJob
from app.models.approval_request import ApprovalRequest
from app.models.subscription_plan import SubscriptionPlan, OrganizationSubscription
from app.models.integration import OrganizationIntegration, IntegrationSyncJob
from app.models.skill import Skill, StudentSkill
from app.models.opportunity import Opportunity, StudentOpportunity
from app.models.application import Application, ApplicationRequirement
from app.models.student_outcome import StudentOutcome
from app.models.career_category import CareerCategory
from app.models.career_skill import CareerSkill, CareerSubject
from app.core.config import settings

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("%", "%%"))
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
