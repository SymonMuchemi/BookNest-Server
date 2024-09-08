"""initial db

Revision ID: af227b412bd4
Revises: 
Create Date: 2024-09-08 12:03:01.722786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af227b412bd4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('books',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('author', sa.String(length=50), nullable=True),
    sa.Column('image_url', sa.Text(), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.Column('rental_fee', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('members',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('debt', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('transaction_type', sa.Enum('return', 'issue', name='transaction_types'), nullable=False),
    sa.Column('date_of_transaction', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['member_id'], ['members.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['books.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('members')
    op.drop_table('books')
    # ### end Alembic commands ###
