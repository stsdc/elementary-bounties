"""Init.

Revision ID: 677c21b65750
Revises: 
Create Date: 2024-11-25 22:13:16.098534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '677c21b65750'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('repositories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('is_visible', sa.Boolean(), nullable=False),
    sa.Column('issues_count', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('repositories', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_repositories_id'), ['id'], unique=False)

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.Text(), nullable=False),
    sa.Column('last_name', sa.Text(), nullable=False),
    sa.Column('email', sa.Text(), nullable=False),
    sa.Column('hashed_password', sa.Text(), nullable=False),
    sa.Column('creation_date', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_id'), ['id'], unique=False)

    op.create_table('issues',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('completed', sa.Boolean(), nullable=False),
    sa.Column('cumulative_bounty', sa.Integer(), nullable=False),
    sa.Column('repository_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('issues', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_issues_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_issues_repository_id'), ['repository_id'], unique=False)

    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('creation_date', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_posts_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_posts_user_id'), ['user_id'], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_posts_user_id'))
        batch_op.drop_index(batch_op.f('ix_posts_id'))

    op.drop_table('posts')
    with op.batch_alter_table('issues', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_issues_repository_id'))
        batch_op.drop_index(batch_op.f('ix_issues_id'))

    op.drop_table('issues')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_id'))

    op.drop_table('users')
    with op.batch_alter_table('repositories', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_repositories_id'))

    op.drop_table('repositories')
    # ### end Alembic commands ###
