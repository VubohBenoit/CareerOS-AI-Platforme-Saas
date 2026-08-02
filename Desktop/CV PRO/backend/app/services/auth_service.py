"""Authentication Service - User signup, login, token management"""

from datetime import datetime, timedelta
from uuid import UUID
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.profile import Profile
from app.config import settings

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""

    # ============================================================================
    # PASSWORD OPERATIONS
    # ============================================================================

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify plain password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    # ============================================================================
    # TOKEN OPERATIONS
    # ============================================================================

    @staticmethod
    def create_access_token(user_id: UUID, expires_delta: int = None) -> str:
        """
        Create JWT access token.

        Args:
            user_id: User's unique ID
            expires_delta: Minutes until expiry (default: 15 min)

        Returns:
            Encoded JWT token
        """
        if expires_delta is None:
            expires_delta = 15  # 15 minutes default

        expire = datetime.utcnow() + timedelta(minutes=expires_delta)

        to_encode = {
            "sub": str(user_id),
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: UUID) -> str:
        """
        Create JWT refresh token.

        Args:
            user_id: User's unique ID

        Returns:
            Encoded JWT token (30 days expiry)
        """
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_EXPIRATION_DAYS
        )

        to_encode = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> UUID:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string
            token_type: "access" or "refresh"

        Returns:
            User ID from token

        Raises:
            ValueError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            # Verify token type
            if payload.get("type") != token_type:
                raise ValueError("Invalid token type")

            user_id_str = payload.get("sub")
            if not user_id_str:
                raise ValueError("Token missing user ID")

            return UUID(user_id_str)

        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")
        except Exception as e:
            raise ValueError(f"Token verification failed: {str(e)}")

    # ============================================================================
    # USER OPERATIONS
    # ============================================================================

    @staticmethod
    def signup(
        db: Session,
        email: str,
        password: str,
        full_name: str
    ) -> dict:
        """
        Register new user account.

        Args:
            db: Database session
            email: User's email
            password: User's password (will be hashed)
            full_name: User's full name

        Returns:
            Dict with user data and tokens

        Raises:
            ValueError: If email already exists or validation fails
        """
        # Validate email format (Pydantic will do this, but double-check)
        if not email or "@" not in email:
            raise ValueError("Invalid email format")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        if not full_name or len(full_name) < 2:
            raise ValueError("Full name required (min 2 characters)")

        # Check email doesn't already exist
        existing_user = db.query(User).filter(User.email == email.lower()).first()
        if existing_user:
            raise ValueError("Email already registered")

        # Create user
        try:
            user = User(
                email=email.lower(),
                hashed_password=AuthService.hash_password(password),
                full_name=full_name,
                is_active=True,
                is_verified=False,  # Email verification not yet implemented
            )

            db.add(user)
            db.flush()  # Get the user ID without committing

            # Create profile (one-to-one relationship)
            profile = Profile(user_id=user.id)
            db.add(profile)

            db.commit()
            db.refresh(user)

            # Generate tokens
            tokens = AuthService._generate_tokens(user.id)

            return {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat(),
                },
                **tokens,
            }

        except IntegrityError:
            db.rollback()
            raise ValueError("Email already registered")
        except Exception as e:
            db.rollback()
            raise ValueError(f"Signup failed: {str(e)}")

    @staticmethod
    def login(db: Session, email: str, password: str) -> dict:
        """
        Authenticate user and return tokens.

        Args:
            db: Database session
            email: User's email
            password: User's password (plain text)

        Returns:
            Dict with user data and tokens

        Raises:
            ValueError: If credentials invalid or user inactive
        """
        # Find user by email (case-insensitive)
        user = db.query(User).filter(User.email == email.lower()).first()

        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not AuthService.verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is disabled")

        # Generate tokens
        tokens = AuthService._generate_tokens(user.id)

        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
            },
            **tokens,
        }

    @staticmethod
    def refresh(db: Session, refresh_token: str) -> dict:
        """
        Issue new access token using refresh token.

        Args:
            db: Database session
            refresh_token: Valid refresh JWT token

        Returns:
            Dict with new access token

        Raises:
            ValueError: If refresh token invalid
        """
        try:
            # Verify refresh token
            user_id = AuthService.verify_token(refresh_token, token_type="refresh")

            # Verify user still exists and is active
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")

            # Generate new access token
            access_token = AuthService.create_access_token(user.id)

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": 900,  # 15 minutes in seconds
            }

        except ValueError:
            raise ValueError("Invalid refresh token")

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """
        Get current user from token.

        Args:
            db: Database session
            token: JWT access token

        Returns:
            User object

        Raises:
            ValueError: If token invalid or user not found
        """
        try:
            user_id = AuthService.verify_token(token, token_type="access")
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                raise ValueError("User not found")

            return user

        except ValueError as e:
            raise ValueError(f"Authentication failed: {str(e)}")

    # ============================================================================
    # PRIVATE HELPERS
    # ============================================================================

    @staticmethod
    def _generate_tokens(user_id: UUID) -> dict:
        """Generate both access and refresh tokens."""
        return {
            "access_token": AuthService.create_access_token(user_id),
            "refresh_token": AuthService.create_refresh_token(user_id),
            "token_type": "bearer",
            "expires_in": 900,  # 15 minutes in seconds
        }
