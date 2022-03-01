"""empty message

Revision ID: 40df4493b7a9
Revises: 8417d81fc859
Create Date: 2022-03-01 01:59:00.563371

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '40df4493b7a9'
down_revision = '8417d81fc859'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('breeds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('city', sa.String(length=20), nullable=True),
    sa.Column('contact', sa.String(length=255), nullable=True),
    sa.Column('info', sa.Text(), nullable=True),
    sa.Column('date_posted', sa.DateTime(), nullable=True),
    sa.Column('poster_id', sa.Integer(), nullable=True),
    sa.Column('category', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category'], ['breeds.id'], ),
    sa.ForeignKeyConstraint(['poster_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('cats2')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cats2',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('category', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('price', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('city', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('contact', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('info', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('date_posted', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('poster_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['poster_id'], ['users.id'], name='cats_poster_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='cats_pkey')
    )
    op.drop_table('cats')
    op.drop_table('breeds')
    # ### end Alembic commands ###