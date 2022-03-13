"""empty message

Revision ID: da9b081b4ee6
Revises: 9bb0a907165d
Create Date: 2022-03-02 01:31:13.329526

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da9b081b4ee6'
down_revision = '9bb0a907165d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cats', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'cats', 'categories', ['category_id'], ['id'])
    op.drop_column('cats', 'categories')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cats', sa.Column('categories', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'cats', type_='foreignkey')
    op.drop_column('cats', 'category_id')
    # ### end Alembic commands ###
