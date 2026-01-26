"""Input validation functions"""
import re
from datetime import date, timedelta

class Validators:
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters"
        if len(username) > 50:
            return False, "Username must be less than 50 characters"
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, _ and -"
        # Check for SQL injection attempts
        dangerous_patterns = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute', 'select', 'insert', 'update', 'delete', 'drop']
        if any(pattern in username. lower() for pattern in dangerous_patterns):
            return False, "Invalid characters in username"
        return True, ""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email: 
            return False, "Email is required"
        if len(email) > 255:
            return False, "Email too long"
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        return True, ""
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters"
        if len(password) > 128:
            return False, "Password too long"
        return True, ""
    
    @staticmethod
    def validate_full_name(name):
        """Validate full name"""
        if not name or len(name) < 2:
            return False, "Name must be at least 2 characters"
        if len(name) > 100:
            return False, "Name too long"
        if not re.match(r'^[a-zA-Z\s]+$', name):
            return False, "Name can only contain letters and spaces"
        return True, ""
    
    @staticmethod
    def validate_target_date(target_date):
        """Validate target date is in future"""
        if not target_date:
            return True, ""  # Optional field
        
        if target_date < date.today():
            return False, "Target date must be in the future"
        
        if target_date > date.today() + timedelta(days=365*2):
            return False, "Target date too far in future (max 2 years)"
        
        return True, ""
    
    @staticmethod
    def validate_hours_per_day(hours):
        """Validate study hours"""
        try:
            hours = float(hours)
            if hours <= 0:
                return False, "Study hours must be greater than 0"
            if hours > 16:
                return False, "Study hours cannot exceed 16 hours per day"
            if hours > 12:
                return True, "⚠️ Warning: 12+ hours/day is very intensive"
            return True, ""
        except: 
            return False, "Invalid hours format"
    
    @staticmethod
    def validate_topics(topics):
        """Validate topics list"""
        if not topics or len(topics) == 0:
            return False, "Please select at least one topic"
        if len(topics) > 10:
            return False, "Maximum 10 topics allowed"
        return True, ""
    
    @staticmethod
    def validate_file_upload(file, allowed_types=['pdf'], max_size_mb=50):
        """Validate uploaded file"""
        if not file:
            return False, "No file provided"
        
        # Check file extension
        file_ext = file.name.split('.')[-1].lower()
        if file_ext not in allowed_types:
            return False, f"Only {', '.join(allowed_types).upper()} files allowed"
        
        # Check file size
        file. seek(0, 2)  # Seek to end
        size_mb = file.tell() / (1024 * 1024)
        file.seek(0)  # Reset
        
        if size_mb > max_size_mb:
            return False, f"File too large (max {max_size_mb}MB, your file:  {size_mb:.1f}MB)"
        
        if size_mb == 0:
            return False, "File is empty"
        
        return True, ""
    
    @staticmethod
    def validate_chat_message(message):
        """Validate chat message"""
        if not message or not message.strip():
            return False, "Message cannot be empty"
        if len(message) > 5000:
            return False, "Message too long (max 5000 characters)"
        return True, ""