"""
Authentication and authorization use cases (core business logic).

These use cases orchestrate the authentication and authorization flows
without depending on specific implementations (hexagonal architecture).
"""

from typing import List
from ports.inbound.auth import Authentication, Authorization
from ports.outbound.auth import IdentityProvider, TokenValidator, PermissionChecker
from ports.models.auth import TokenData, UserInfo

from config.logger import logger


class AuthenticationImpl(Authentication):
    """
    Implementation of authentication use cases.
    
    Depends on abstractions (ports) rather than concrete implementations.
    """
    
    def __init__(
        self,
        identity_provider: IdentityProvider,
        token_validator: TokenValidator
    ):
        self.identity_provider = identity_provider
        self.token_validator = token_validator
    
    async def authenticate_with_provider(
        self,
        provider_code: str,
        state: str
    ) -> UserInfo:
        """
        Authenticate user using external identity provider.
        
        Business rules:
        - Exchange code for access token
        - Retrieve user information
        - Log authentication attempt
        """
        logger.info(f"Authenticating user with provider code")
        
        try:
            # Exchange authorization code for access token
            access_token = await self.identity_provider.exchange_code(provider_code)
            
            # Get user information from provider
            user_info = await self.identity_provider.get_user_info(access_token)
            
            logger.info(f"Successfully authenticated user: {user_info.username}")
            return user_info
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise ValueError(f"Authentication failed: {e}")
    
    async def validate_access_token(self, token: str) -> TokenData:
        """
        Validate an access token and return user information.
        
        Business rules:
        - Token must be active
        - Token must not be expired
        """
        logger.debug("Validating access token")
        
        try:
            token_data = await self.token_validator.introspect_token(token)
            
            if not token_data.active:
                raise ValueError("Token is not active")
            
            logger.debug(f"Token validated for user: {token_data.username}")
            return token_data
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            raise ValueError(f"Invalid token: {e}")


class AuthorizationImpl(Authorization):
    """
    Implementation of authorization use cases.
    
    Depends on PermissionChecker abstraction.
    """
    
    def __init__(self, permission_checker: PermissionChecker):
        self.permission_checker = permission_checker
    
    async def check_user_access(
        self,
        username: str,
        required_permission: str
    ) -> bool:
        """
        Check if user has the required permission.
        
        Business rules:
        - User must have explicit permission grant
        - Or user must have permission through role membership
        """
        logger.debug(
            f"Checking access: user={username}, permission={required_permission}"
        )
        
        try:
            has_permission = await self.permission_checker.check_permission(
                username,
                required_permission
            )
            
            if has_permission:
                logger.info(
                    f"Access granted: user={username}, permission={required_permission}"
                )
            else:
                logger.warning(
                    f"Access denied: user={username}, permission={required_permission}"
                )
            
            return has_permission
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            # Fail-safe: deny access on error
            return False
    
    async def get_user_authorized_scopes(
        self,
        username: str,
        requested_scopes: List[str]
    ) -> List[str]:
        """
        Filter requested scopes to only those the user has permission for.
        
        Business rules:
        - Each scope maps to a permission (e.g., "data:read" scope = "data:read" permission)
        - Only grant scopes the user actually has permission for
        - Log which scopes were filtered out
        """
        logger.info(
            f"Filtering scopes for user={username}, requested={len(requested_scopes)}"
        )
        
        try:
            # Get all user permissions
            user_permissions = await self.permission_checker.get_user_permissions(
                username
            )
            
            # Filter requested scopes to only authorized ones
            # Scope naming convention: scope maps 1:1 to permission
            authorized_scopes = [
                scope for scope in requested_scopes
                if scope in user_permissions
            ]
            
            filtered_count = len(requested_scopes) - len(authorized_scopes)
            if filtered_count > 0:
                logger.info(
                    f"Filtered {filtered_count} unauthorized scopes for user={username}"
                )
            
            logger.info(
                f"Authorized scopes for user={username}: {authorized_scopes}"
            )
            
            return authorized_scopes
            
        except Exception as e:
            logger.error(f"Error filtering scopes: {e}")
            # Fail-safe: return empty scope list on error
            return []
