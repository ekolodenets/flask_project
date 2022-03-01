"""empty message

Revision ID: 2bb832de1c8b
Revises: 31549f78c13b
Create Date: 2022-03-01 01:24:32.984434

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2bb832de1c8b'
down_revision = '31549f78c13b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('breeds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('posts')
    op.add_column('cats', sa.Column('poster_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'cats', 'users', ['poster_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'cats', type_='foreignkey')
    op.drop_column('cats', 'poster_id')
    op.create_table('posts',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('author', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('date_posted', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='posts_pkey')
    )
    op.drop_table('breeds')
    # ### end Alembic commands ###
