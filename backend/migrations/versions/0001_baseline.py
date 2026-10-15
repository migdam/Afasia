"""The schema as it was when migrations began: what create_all made.

Revision ID: 0001
Revises:
Created: 2026-10-15

Databases made before migrations (backlog P3-1) were made by create_all,
which added the tables that were new in each version of the app. This
migration creates only the tables a database doesn't have yet, so it brings
those databases, and empty ones, to the same schema without touching data.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

ENUMS = {
    "userrole": ("PATIENT", "THERAPIST", "ADMIN"),
    "exercisetype": ("WORD_NAMING", "SENTENCE_COMPLETION", "IMAGE_RECOGNITION", "PRONUNCIATION"),
    "difficultylevel": ("EASY", "MEDIUM", "HARD"),
    "badgetype": ("FIRST_SESSION", "WEEK_STREAK", "MONTH_STREAK"),
}


def enum(name):
    """An enum column type. On PostgreSQL its type is made once, before the
    tables (upgrade), so tables that share it don't each try to make it."""
    values = ENUMS[name]
    return sa.Enum(*values, name=name).with_variant(
        postgresql.ENUM(*values, name=name, create_type=False), "postgresql")


USER_ROLE = enum("userrole")
EXERCISE_TYPE = enum("exercisetype")
DIFFICULTY = enum("difficultylevel")
BADGE_TYPE = enum("badgetype")


def missing(table):
    return table not in sa.inspect(op.get_bind()).get_table_names()


def upgrade():
    if op.get_bind().dialect.name == "postgresql":
        for name, values in ENUMS.items():
            postgresql.ENUM(*values, name=name).create(op.get_bind(), checkfirst=True)

    if missing("consents"):
        op.create_table('consents',
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('kind', sa.String(length=32), nullable=False),
            sa.Column('granted', sa.Boolean(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('user_id', 'kind')
        )

    if missing("login_cutoffs"):
        op.create_table('login_cutoffs',
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('not_before', sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint('user_id')
        )

    if missing("revoked_logins"):
        op.create_table('revoked_logins',
            sa.Column('sid', sa.String(length=64), nullable=False),
            sa.Column('expires_at', sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint('sid')
        )
        with op.batch_alter_table('revoked_logins', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_revoked_logins_expires_at'), ['expires_at'], unique=False)

    if missing("time_zones"):
        op.create_table('time_zones',
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('time_zone', sa.String(length=64), nullable=False),
            sa.PrimaryKeyConstraint('user_id')
        )

    if missing("users"):
        op.create_table('users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(), nullable=False),
            sa.Column('username', sa.String(), nullable=False),
            sa.Column('hashed_password', sa.String(), nullable=False),
            sa.Column('full_name', sa.String(), nullable=True),
            sa.Column('language', sa.String(), nullable=True),
            sa.Column('role', USER_ROLE, nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.Column('total_points', sa.Integer(), nullable=True),
            sa.Column('current_streak', sa.Integer(), nullable=True),
            sa.Column('longest_streak', sa.Integer(), nullable=True),
            sa.Column('last_activity_date', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
            batch_op.create_index(batch_op.f('ix_users_id'), ['id'], unique=False)
            batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    if missing("progress"):
        op.create_table('progress',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('date', sa.DateTime(), nullable=True),
            sa.Column('exercises_completed', sa.Integer(), nullable=True),
            sa.Column('accuracy_rate', sa.Float(), nullable=True),
            sa.Column('total_time_seconds', sa.Integer(), nullable=True),
            sa.Column('points_earned', sa.Integer(), nullable=True),
            sa.Column('difficulty_level', DIFFICULTY, nullable=True),
            sa.Column('exercise_type', EXERCISE_TYPE, nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('progress', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_progress_id'), ['id'], unique=False)

    if missing("scheduled_sessions"):
        op.create_table('scheduled_sessions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('scheduled_time', sa.DateTime(), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('exercise_type', EXERCISE_TYPE, nullable=True),
            sa.Column('difficulty', DIFFICULTY, nullable=True),
            sa.Column('is_completed', sa.Boolean(), nullable=True),
            sa.Column('reminder_sent', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('scheduled_sessions', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_scheduled_sessions_id'), ['id'], unique=False)

    if missing("therapy_sessions"):
        op.create_table('therapy_sessions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('exercise_type', EXERCISE_TYPE, nullable=False),
            sa.Column('difficulty', DIFFICULTY, nullable=True),
            sa.Column('language', sa.String(), nullable=True),
            sa.Column('total_exercises', sa.Integer(), nullable=True),
            sa.Column('completed_exercises', sa.Integer(), nullable=True),
            sa.Column('score', sa.Float(), nullable=True),
            sa.Column('duration_seconds', sa.Integer(), nullable=True),
            sa.Column('started_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('is_completed', sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('therapy_sessions', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_therapy_sessions_id'), ['id'], unique=False)

    if missing("user_badges"):
        op.create_table('user_badges',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('badge_type', BADGE_TYPE, nullable=False),
            sa.Column('earned_at', sa.DateTime(), nullable=True),
            sa.Column('details', sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('user_badges', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_user_badges_id'), ['id'], unique=False)

    if missing("exercises"):
        op.create_table('exercises',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('session_id', sa.Integer(), nullable=False),
            sa.Column('exercise_type', EXERCISE_TYPE, nullable=False),
            sa.Column('difficulty', DIFFICULTY, nullable=True),
            sa.Column('question', sa.Text(), nullable=False),
            sa.Column('correct_answer', sa.String(), nullable=False),
            sa.Column('user_answer', sa.String(), nullable=True),
            sa.Column('image_url', sa.String(), nullable=True),
            sa.Column('audio_url', sa.String(), nullable=True),
            sa.Column('options', sa.JSON(), nullable=True),
            sa.Column('is_correct', sa.Boolean(), nullable=True),
            sa.Column('time_taken_seconds', sa.Integer(), nullable=True),
            sa.Column('attempts', sa.Integer(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['session_id'], ['therapy_sessions.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('exercises', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_exercises_id'), ['id'], unique=False)

    if missing("audio_recordings"):
        op.create_table('audio_recordings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('exercise_id', sa.Integer(), nullable=True),
            sa.Column('file_path', sa.String(), nullable=False),
            sa.Column('duration_seconds', sa.Float(), nullable=True),
            sa.Column('transcription', sa.Text(), nullable=True),
            sa.Column('accuracy_score', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('audio_recordings', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_audio_recordings_id'), ['id'], unique=False)

    if missing("exercise_choices"):
        op.create_table('exercise_choices',
            sa.Column('exercise_id', sa.Integer(), nullable=False),
            sa.Column('words', sa.JSON(), nullable=False),
            sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
            sa.PrimaryKeyConstraint('exercise_id')
        )

    if missing("exercise_cues"):
        op.create_table('exercise_cues',
            sa.Column('exercise_id', sa.Integer(), nullable=False),
            sa.Column('level', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
            sa.PrimaryKeyConstraint('exercise_id')
        )

    if missing("exercise_tiles"):
        op.create_table('exercise_tiles',
            sa.Column('exercise_id', sa.Integer(), nullable=False),
            sa.Column('letters', sa.JSON(), nullable=False),
            sa.ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ),
            sa.PrimaryKeyConstraint('exercise_id')
        )


def downgrade():
    op.drop_table('exercise_tiles')
    op.drop_table('exercise_cues')
    op.drop_table('exercise_choices')
    with op.batch_alter_table('audio_recordings', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_audio_recordings_id'))

    op.drop_table('audio_recordings')
    with op.batch_alter_table('exercises', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_exercises_id'))

    op.drop_table('exercises')
    with op.batch_alter_table('user_badges', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_badges_id'))

    op.drop_table('user_badges')
    with op.batch_alter_table('therapy_sessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_therapy_sessions_id'))

    op.drop_table('therapy_sessions')
    with op.batch_alter_table('scheduled_sessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_scheduled_sessions_id'))

    op.drop_table('scheduled_sessions')
    with op.batch_alter_table('progress', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_progress_id'))

    op.drop_table('progress')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_id'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    op.drop_table('time_zones')
    with op.batch_alter_table('revoked_logins', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_revoked_logins_expires_at'))

    op.drop_table('revoked_logins')
    op.drop_table('login_cutoffs')
    op.drop_table('consents')
    # PostgreSQL keeps enum types after their tables are gone.
    for name in ("badgetype", "exercisetype", "difficultylevel", "userrole"):
        postgresql.ENUM(name=name).drop(op.get_bind(), checkfirst=True)
