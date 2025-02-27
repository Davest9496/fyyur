"""Initial migration

Revision ID: 86f6ba57931e
Revises: 
Create Date: 2025-02-26 11:11:59.800365

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86f6ba57931e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('availability',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('day_of_week', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('artists', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website_link', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.drop_column('website')

    with op.batch_alter_table('shows', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.Integer(), nullable=False))

    with op.batch_alter_table('venues', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website_link', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.drop_column('website')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('venues', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
        batch_op.drop_column('created_at')
        batch_op.drop_column('website_link')

    with op.batch_alter_table('shows', schema=None) as batch_op:
        batch_op.drop_column('id')

    with op.batch_alter_table('artists', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
        batch_op.drop_column('created_at')
        batch_op.drop_column('website_link')

    op.drop_table('availability')
    # ### end Alembic commands ###
