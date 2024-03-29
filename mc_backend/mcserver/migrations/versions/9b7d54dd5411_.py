"""empty message

Revision ID: 9b7d54dd5411
Revises: 905858a5c465
Create Date: 2020-05-15 15:07:47.573520

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9b7d54dd5411'
down_revision = '905858a5c465'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('Corpus_uri_key', 'Corpus', type_='unique')
    op.drop_column('Corpus', 'uri')
    op.alter_column('Exercise', 'correct_feedback',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('Exercise', 'exercise_type_translation',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('Exercise', 'general_feedback',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('Exercise', 'incorrect_feedback',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('Exercise', 'instructions',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('Exercise', 'language',
                    existing_type=sa.VARCHAR(),
                    nullable=False,
                    existing_server_default=sa.text("'de'::character varying"))
    op.alter_column('Exercise', 'last_access_time',
                    existing_type=postgresql.TIMESTAMP(), type_=sa.FLOAT(),
                    postgresql_using="date_part('epoch',last_access_time)::float", nullable=False)
    op.alter_column('Exercise', 'partially_correct_feedback',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('Exercise', 'search_values',
                    existing_type=sa.VARCHAR(),
                    nullable=False,
                    existing_server_default=sa.text("''::character varying"))
    op.alter_column('Exercise', 'text_complexity',
                    existing_type=postgresql.DOUBLE_PRECISION(precision=53),
                    nullable=False,
                    existing_server_default=sa.text("'0'::double precision"))
    op.alter_column('Exercise', 'work_author',
                    existing_type=sa.VARCHAR(),
                    nullable=False,
                    existing_server_default=sa.text("''::character varying"))
    op.alter_column('Exercise', 'work_title',
                    existing_type=sa.VARCHAR(),
                    nullable=False,
                    existing_server_default=sa.text("''::character varying"))
    op.drop_constraint('Exercise_uri_key', 'Exercise', type_='unique')
    op.drop_column('Exercise', 'uri')
    op.alter_column('LearningResult', 'actor_account_name',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'actor_object_type',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'category_id',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'category_object_type',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'choices',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'completion',
                    existing_type=sa.BOOLEAN(),
                    nullable=False)
    op.alter_column('LearningResult', 'correct_responses_pattern',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'created_time',
                    existing_type=postgresql.TIMESTAMP(), type_=sa.FLOAT(),
                    postgresql_using="date_part('epoch',created_time)::float")
    op.alter_column('LearningResult', 'duration',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'extensions',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'interaction_type',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'object_definition_description',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'object_definition_type',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'object_object_type',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'response',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'score_max',
                    existing_type=sa.INTEGER(),
                    nullable=False)
    op.alter_column('LearningResult', 'score_min',
                    existing_type=sa.INTEGER(),
                    nullable=False)
    op.alter_column('LearningResult', 'score_raw',
                    existing_type=sa.INTEGER(),
                    nullable=False)
    op.alter_column('LearningResult', 'score_scaled',
                    existing_type=postgresql.DOUBLE_PRECISION(precision=53),
                    nullable=False)
    op.alter_column('LearningResult', 'success',
                    existing_type=sa.BOOLEAN(),
                    nullable=False)
    op.alter_column('LearningResult', 'verb_display',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('LearningResult', 'verb_id',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
    op.alter_column('UpdateInfo', 'created_time',
                    existing_type=postgresql.TIMESTAMP(), type_=sa.FLOAT(),
                    postgresql_using="date_part('epoch',created_time)::float", nullable=False)
    op.alter_column('UpdateInfo', 'last_modified_time',
                    existing_type=postgresql.TIMESTAMP(), type_=sa.FLOAT(),
                    postgresql_using="date_part('epoch',last_modified_time)::float", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('UpdateInfo', 'last_modified_time', existing_type=sa.FLOAT(),
                    type_=postgresql.TIMESTAMP(),
                    postgresql_using="to_timestamp(last_modified_time)", nullable=True)
    op.alter_column('UpdateInfo', 'created_time',
                    existing_type=sa.FLOAT(), postgresql_using="to_timestamp(created_time)",
                    type_=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('LearningResult', 'verb_id',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'verb_display',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'success',
                    existing_type=sa.BOOLEAN(),
                    nullable=True)
    op.alter_column('LearningResult', 'score_scaled',
                    existing_type=postgresql.DOUBLE_PRECISION(precision=53),
                    nullable=True)
    op.alter_column('LearningResult', 'score_raw',
                    existing_type=sa.INTEGER(),
                    nullable=True)
    op.alter_column('LearningResult', 'score_min',
                    existing_type=sa.INTEGER(),
                    nullable=True)
    op.alter_column('LearningResult', 'score_max',
                    existing_type=sa.INTEGER(),
                    nullable=True)
    op.alter_column('LearningResult', 'response',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'object_object_type',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'object_definition_type',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'object_definition_description',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'interaction_type',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'extensions',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'duration',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'created_time',
                    existing_type=sa.FLOAT(), postgresql_using="to_timestamp(created_time)",
                    type_=postgresql.TIMESTAMP())
    op.alter_column('LearningResult', 'correct_responses_pattern',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'completion',
                    existing_type=sa.BOOLEAN(),
                    nullable=True)
    op.alter_column('LearningResult', 'choices',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'category_object_type',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'category_id',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'actor_object_type',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('LearningResult', 'actor_account_name',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.add_column(
        'Exercise', sa.Column('uri', sa.VARCHAR(), autoincrement=False, nullable=False,
                              server_default=sa.text("random()")))
    op.create_unique_constraint('Exercise_uri_key', 'Exercise', ['uri'])
    op.alter_column('Exercise', 'work_title',
                    existing_type=sa.VARCHAR(),
                    nullable=True,
                    existing_server_default=sa.text("''::character varying"))
    op.alter_column('Exercise', 'work_author',
                    existing_type=sa.VARCHAR(),
                    nullable=True,
                    existing_server_default=sa.text("''::character varying"))
    op.alter_column('Exercise', 'text_complexity',
                    existing_type=postgresql.DOUBLE_PRECISION(precision=53),
                    nullable=True,
                    existing_server_default=sa.text("'0'::double precision"))
    op.alter_column('Exercise', 'search_values',
                    existing_type=sa.VARCHAR(),
                    nullable=True,
                    existing_server_default=sa.text("''::character varying"))
    op.alter_column('Exercise', 'partially_correct_feedback',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('Exercise', 'last_access_time',
                    existing_type=sa.FLOAT(), postgresql_using="to_timestamp(last_access_time)",
                    type_=postgresql.TIMESTAMP(), nullable=True)
    op.alter_column('Exercise', 'language',
                    existing_type=sa.VARCHAR(),
                    nullable=True,
                    existing_server_default=sa.text("'de'::character varying"))
    op.alter_column('Exercise', 'instructions',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('Exercise', 'incorrect_feedback',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('Exercise', 'general_feedback',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('Exercise', 'exercise_type_translation',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.alter_column('Exercise', 'correct_feedback',
                    existing_type=sa.VARCHAR(),
                    nullable=True)
    op.add_column('Corpus', sa.Column('uri', sa.VARCHAR(), autoincrement=False, nullable=False,
                                      server_default=sa.text("random()")))
    op.create_unique_constraint('Corpus_uri_key', 'Corpus', ['uri'])
    # ### end Alembic commands ###
