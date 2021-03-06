"""empty message

Revision ID: 4b568895bc48
Revises: f4edf67ed115
Create Date: 2022-03-01 01:47:17.603964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b568895bc48'
down_revision = 'f4edf67ed115'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('breeds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('cats', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint('cats_poster_id_fkey', 'cats', type_='foreignkey')
    op.create_foreign_key(None, 'cats', 'users', ['user_id'], ['id'])
    op.drop_column('cats', 'poster_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cats', sa.Column('poster_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'cats', type_='foreignkey')
    op.create_foreign_key('cats_poster_id_fkey', 'cats', 'users', ['poster_id'], ['id'])
    op.drop_column('cats', 'user_id')
    op.drop_table('breeds')
    # ### end Alembic commands ###
