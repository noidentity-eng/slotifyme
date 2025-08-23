"""Update plan model with new domain fields

Revision ID: 001
Revises: 
Create Date: 2025-08-22 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade to new plan model with domain fields."""
    
    # Add new columns to plans table
    op.add_column('plans', sa.Column('overage_policy_json', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'))
    op.add_column('plans', sa.Column('pricing_ref', sa.String(), nullable=True))
    
    # Add pricing_ref column to tenant_plans table
    op.add_column('tenant_plans', sa.Column('pricing_ref', sa.String(), nullable=True))
    
    # Transform existing data
    connection = op.get_bind()
    
    # Update plans table - transform limits_json and features_json
    plans = connection.execute(sa.text("SELECT code, limits_json, features_json FROM plans")).fetchall()
    
    for plan in plans:
        code, limits_json, features_json = plan
        
        # Transform limits_json
        new_limits = {}
        if limits_json:
            # Map old fields to new
            if 'max_locations' in limits_json:
                new_limits['locations_included'] = limits_json['max_locations']
            if 'max_staff_accounts' in limits_json:
                new_limits['stylists_included'] = limits_json['max_staff_accounts']
            # Drop legacy fields: max_bookings_per_month, max_customers
        
        # Transform features_json
        new_features = {}
        if features_json:
            # Keep advanced_analytics if present
            if 'advanced_analytics' in features_json:
                new_features['advanced_analytics'] = features_json['advanced_analytics']
            # Remove legacy fields: online_booking, sms_notifications, custom_branding, multi_location
        
        # Set default overage policy
        overage_policy = {
            "allow_extra_locations": True,
            "allow_extra_stylists": True
        }
        
        # Update the plan
        connection.execute(
            sa.text("""
                UPDATE plans 
                SET limits_json = :limits, 
                    features_json = :features, 
                    overage_policy_json = :overage_policy,
                    pricing_ref = NULL
                WHERE code = :code
            """),
            {
                'limits': new_limits,
                'features': new_features,
                'overage_policy': overage_policy,
                'code': code
            }
        )


def downgrade():
    """Downgrade to old plan model."""
    
    # Remove new columns from tenant_plans
    op.drop_column('tenant_plans', 'pricing_ref')
    
    # Remove new columns from plans
    op.drop_column('plans', 'pricing_ref')
    op.drop_column('plans', 'overage_policy_json')
    
    # Note: We don't restore the old limits_json and features_json structure
    # as this would require complex reverse transformation logic
    # The data will remain in the new format
