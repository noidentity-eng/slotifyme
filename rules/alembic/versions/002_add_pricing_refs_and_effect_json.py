"""Add pricing references and effect_json

Revision ID: 002
Revises: 001
Create Date: 2025-08-22 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Add pricing references and effect_json fields."""
    
    # Add new columns to addons table
    op.add_column('addons', sa.Column('effect_json', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'))
    op.add_column('addons', sa.Column('pricing_ref', sa.String(), nullable=True))
    
    # Add pricing_ref column to tenant_addons table
    op.add_column('tenant_addons', sa.Column('pricing_ref', sa.String(), nullable=True))
    
    # Create overage_price_refs table
    op.create_table('overage_price_refs',
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('per_stylist_ref', sa.String(), nullable=True),
        sa.Column('per_location_ref', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('tenant_id')
    )
    op.create_index(op.f('ix_overage_price_refs_tenant_id'), 'overage_price_refs', ['tenant_id'], unique=False)
    
    # Backfill effect_json for existing addons
    connection = op.get_bind()
    
    # Get existing addons and backfill effect_json based on their meta_json
    addons = connection.execute(sa.text("SELECT code, meta_json FROM addons")).fetchall()
    
    for addon in addons:
        code, meta_json = addon
        
        # Default effect_json based on addon code
        effect_json = {}
        
        if code == "ai_booking":
            effect_json = {"ai_booking": True}
        elif code == "variable_pricing":
            effect_json = {"variable_pricing": True}
        elif code == "value_pack":
            effect_json = {"packages": True, "upsell": True, "waitlist": True, "gift_cards": True}
        elif code == "family_booking":
            effect_json = {"family_booking": True}
        elif code == "gift_cards":
            effect_json = {"gift_cards": True}
        
        # Update the addon
        connection.execute(
            sa.text("""
                UPDATE addons 
                SET effect_json = :effect_json,
                    pricing_ref = NULL
                WHERE code = :code
            """),
            {
                'effect_json': effect_json,
                'code': code
            }
        )


def downgrade():
    """Remove pricing references and effect_json fields."""
    
    # Drop overage_price_refs table
    op.drop_index(op.f('ix_overage_price_refs_tenant_id'), table_name='overage_price_refs')
    op.drop_table('overage_price_refs')
    
    # Remove columns from tenant_addons
    op.drop_column('tenant_addons', 'pricing_ref')
    
    # Remove columns from addons
    op.drop_column('addons', 'pricing_ref')
    op.drop_column('addons', 'effect_json')
