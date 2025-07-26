#!/usr/bin/env python3
"""
Database table creation script for LifeSync collaboration features.
Run this script to create the new collaboration tables.
"""

from app.core.database import engine, Base
from app.models.models import *  # Import existing models
from app.models.collaboration_models import *  # Import collaboration models

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
    
    # List all created tables
    print("\nCreated tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    create_tables()