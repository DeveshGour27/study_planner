import bcrypt
import jwt
from datetime import datetime, timedelta
from database.models import User, StudentProfile
from database.db_manager import SessionLocal
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days


class AuthManager:
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def create_jwt_token(user_id: str) -> str:
        """Create JWT token for user"""
        payload = {
            'user_id':  user_id,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime. utcnow()
        }
        return jwt. encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_jwt_token(token: str) -> dict:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def register_user(username:  str, email: str, password:  str, full_name: str, age_group: str = None):
        """Register new user with proper transaction handling"""
        db = SessionLocal()
        try:
            # Check if username exists
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                return False, "Username already exists", None
            
            # Check if email exists
            existing_email = db.query(User).filter(User.email == email).first()
            if existing_email:  
                return False, "Email already exists", None
            
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user with age_group
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password. decode('utf-8'),
                full_name=full_name,
                age_group=age_group  # ← Now this will work
            )
            
            db.add(new_user)
            db.flush()
            
            # Create profile with manual timestamps
            now = datetime.utcnow()
            
            new_profile = StudentProfile(
                user_id=new_user. user_id,
                topics_to_learn=[],
                hours_per_day=4,
                current_day_number=1,
                total_planned_days=30,
                streak_count=0,
                current_levels={},
                onboarding_completed=False,
                created_at=now,
                updated_at=now
            )
            
            db.add(new_profile)
            db.commit()
            
            print(f"✅ User registered:  {username}")
            return True, "Registration successful!", new_user. user_id
            
        except Exception as e:
            db. rollback()
            print(f"❌ Registration error: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Registration failed: {str(e)}", None
        finally:
            db.close()
    
    @staticmethod
    def verify_credentials(username: str, password: str) -> bool:
        """Verify user credentials"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                return False
            
            return AuthManager.verify_password(password, user.password_hash)
        finally:
            db.close()
    
    @staticmethod
    def login_user(username:  str, password: str) -> tuple: 
        """
        Login user
        Returns:  (success:  bool, message: str, token: str or None, user:  User or None)
        """
        db = SessionLocal()
        try:
            # Find user by username or email
            user = db.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user: 
                return False, "Invalid username or password", None, None
            
            if not user.is_active:
                return False, "Account is deactivated", None, None
            
            # Verify password
            if not AuthManager.verify_password(password, user.password_hash):
                return False, "Invalid username or password", None, None
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            # Create JWT token
            token = AuthManager. create_jwt_token(user. user_id)
            
            return True, "Login successful!", token, user
            
        except Exception as e:
            return False, f"Login failed: {str(e)}", None, None
        finally:
            db. close()
    
    @staticmethod
    def get_user_by_id(user_id: str):
        """Get user by ID"""
        db = SessionLocal()
        try:
            return db.query(User).filter(User.user_id == user_id).first()
        finally:
            db.close()
    
    @staticmethod
    def get_user_profile(user_id: str):
        """Get user profile"""
        db = SessionLocal()
        try:
            return db. query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        finally:
            db.close()