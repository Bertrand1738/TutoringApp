"""
Examine URL patterns in Django project
"""
import os
import sys
import django
import re

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

def print_url_patterns():
    """Print all URL patterns in the Django project"""
    print("URL patterns in the Django project:")
    print("=" * 70)
    
    resolver = get_resolver()
    all_patterns = extract_patterns(resolver.url_patterns)
    
    # Sort by URL pattern
    all_patterns.sort(key=lambda x: x[0])
    
    # Print patterns
    for pattern, view_name, app_name in all_patterns:
        print(f"{pattern:<50} {view_name:<30} {app_name}")

def extract_patterns(patterns, prefix="", app_name=None):
    """Extract all URL patterns from a list of URL patterns"""
    result = []
    for pattern in patterns:
        if isinstance(pattern, URLPattern):
            # Get the pattern string
            pattern_str = prefix + str(pattern.pattern)
            pattern_str = pattern_str.replace("^", "").replace("$", "")
            
            # Remove regex patterns for clarity
            pattern_str = re.sub(r'\(\?P<[^>]+>[^)]+\)', ':id', pattern_str)
            
            # Get the view name
            view_name = pattern.callback.__name__ if hasattr(pattern.callback, "__name__") else str(pattern.callback)
            
            # Add to result
            result.append((pattern_str, view_name, app_name or ""))
            
        elif isinstance(pattern, URLResolver):
            # Get namespace and new prefix
            new_app_name = pattern.app_name or app_name
            new_prefix = prefix + str(pattern.pattern)
            new_prefix = new_prefix.replace("^", "").replace("$", "")
            
            # Recursively extract patterns
            result.extend(extract_patterns(pattern.url_patterns, new_prefix, new_app_name))
    
    return result

if __name__ == "__main__":
    print_url_patterns()
