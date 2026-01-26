"""Helper functions for safe data handling"""

def safe_percentage(value, total, default=0):
    """Safely calculate percentage"""
    try:
        if total is None or total == 0:
            return default
        if value is None: 
            return default
        return (value / total) * 100
    except:
        return default

def safe_format(value, format_string="{:.1f}", default="N/A"):
    """Safely format a value"""
    try:
        if value is None:
            return default
        return format_string. format(value)
    except:
        return default

def safe_get_attr(obj, attr, default=None):
    """Safely get attribute from object"""
    try:
        value = getattr(obj, attr, default)
        return value if value is not None else default
    except:
        return default

def safe_dict_get(dictionary, key, default=None):
    """Safely get value from dictionary"""
    try: 
        if not dictionary:
            return default
        return dictionary.get(key, default)
    except:
        return default

def safe_list_get(lst, index, default=None):
    """Safely get item from list"""
    try: 
        if not lst or index >= len(lst):
            return default
        return lst[index]
    except:
        return default

def truncate_text(text, max_length=100, suffix="..."):
    """Safely truncate text"""
    try:
        if not text: 
            return ""
        if len(text) <= max_length:
            return text
        return text[: max_length - len(suffix)] + suffix
    except:
        return str(text)[:max_length]