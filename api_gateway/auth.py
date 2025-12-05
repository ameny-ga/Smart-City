# Ajout d'un système d'authentification simple avec 2 rôles

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
import secrets

security = HTTPBasic()

# Base de données des utilisateurs (en production: utiliser une vraie DB)
USERS_DB = {
    "admin": {
        "username": "admin",
        "password": "admin123",  # En production: utiliser bcrypt pour hasher
        "role": "admin",
        "full_name": "Administrateur Ville"
    },
    "user": {
        "username": "user",
        "password": "user123",
        "role": "user",
        "full_name": "Utilisateur"
    }
}

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Vérifie les identifiants de l'utilisateur."""
    user = USERS_DB.get(credentials.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Vérification du mot de passe (en production: utiliser bcrypt.checkpw)
    is_correct_password = secrets.compare_digest(
        credentials.password.encode('utf-8'),
        user["password"].encode('utf-8')
    )
    
    if not is_correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user

def require_admin(user: dict = Depends(verify_credentials)):
    """Vérifie que l'utilisateur a le rôle admin."""
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return user

def get_current_user_optional() -> Optional[dict]:
    """Retourne l'utilisateur courant ou None si non authentifié."""
    # Pour les endpoints publics
    return None
