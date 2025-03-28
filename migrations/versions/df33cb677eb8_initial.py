"""initial

Revision ID: df33cb677eb8
Revises: 
Create Date: 2025-03-15 13:10:54.928114

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df33cb677eb8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('password_hash', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('research_profile',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('problem_statement', sa.Text(), nullable=False),
    sa.Column('search_suffix', sa.String(length=200), nullable=True),
    sa.Column('max_pdfs_per_topic', sa.Integer(), nullable=True),
    sa.Column('focus', sa.String(length=20), nullable=True),
    sa.Column('academic_format', sa.Boolean(), nullable=True),
    sa.Column('language', sa.String(length=10), nullable=True),
    sa.Column('search_url', sa.String(length=500), nullable=False),
    sa.Column('is_template', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('research_profile')
    op.drop_table('user')
    # ### end Alembic commands ###
