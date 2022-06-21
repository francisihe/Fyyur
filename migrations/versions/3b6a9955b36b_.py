"""empty message

Revision ID: 3b6a9955b36b
Revises: b39e974b1745
Create Date: 2022-06-13 03:00:18.853592

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b6a9955b36b'
down_revision = 'b39e974b1745'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('Artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('Artist', sa.Column('looking_for_venues', sa.String(length=120), nullable=True))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('Venue', sa.Column('looking_for_talent', sa.String(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'looking_for_talent')
    op.drop_column('Venue', 'website_link')
    op.drop_column('Venue', 'genres')
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'looking_for_venues')
    op.drop_column('Artist', 'website_link')
    op.drop_table('Show')
    # ### end Alembic commands ###