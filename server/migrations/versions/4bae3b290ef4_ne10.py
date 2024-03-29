"""ne10

Revision ID: 4bae3b290ef4
Revises: d654aba99230
Create Date: 2023-11-07 23:58:10.493089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4bae3b290ef4'
down_revision = 'd654aba99230'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.drop_column('Comments')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Comments', sa.VARCHAR(), nullable=True))

    # ### end Alembic commands ###
