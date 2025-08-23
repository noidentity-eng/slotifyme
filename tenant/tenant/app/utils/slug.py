"""Slug utilities for tenant and location names."""

import re
import unicodedata
from typing import List


# Reserved words that cannot be used as slugs
RESERVED_WORDS = {
    "admin", "api", "www", "internal", "public", "health", "stats",
    "tenants", "locations", "users", "links"
}


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text


def is_valid_slug(slug: str) -> bool:
    """Check if a slug is valid."""
    if not slug:
        return False
    
    # Check if it's a reserved word
    if slug.lower() in RESERVED_WORDS:
        return False
    
    # Check if it contains only valid characters
    if not re.match(r'^[a-z0-9-]+$', slug):
        return False
    
    # Check if it starts or ends with hyphen
    if slug.startswith('-') or slug.endswith('-'):
        return False
    
    # Check if it's too short or too long
    if len(slug) < 2 or len(slug) > 50:
        return False
    
    return True


def generate_unique_slug(base_name: str, existing_slugs: List[str]) -> str:
    """Generate a unique slug from a base name."""
    base_slug = slugify(base_name)
    
    if not base_slug:
        base_slug = "untitled"
    
    # If the base slug is already unique, return it
    if base_slug not in existing_slugs:
        return base_slug
    
    # Try with numbers until we find a unique one
    counter = 1
    while True:
        candidate = f"{base_slug}-{counter}"
        if candidate not in existing_slugs:
            return candidate
        counter += 1
