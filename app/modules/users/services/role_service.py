from sqlalchemy.orm import Session
from app.modules.users.models.role import Role, Permission
from typing import List, Optional
from app.modules.common.config.database import Base, engine

class RoleService:
    @staticmethod
    def create_role(db: Session, name: str, description: str) -> Role:
        role = Role(name=name, description=description)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def create_permission(db: Session, name: str, description: str) -> Permission:
        permission = Permission(name=name, description=description)
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission

    @staticmethod
    def get_role(db: Session, role_id: int) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def get_permission(db: Session, permission_id: int) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.id == permission_id).first()

    @staticmethod
    def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.name == name).first()

    @staticmethod
    def add_permission_to_role(
        db: Session,
        role: Role,
        permission: Permission
    ) -> Role:
        role.permissions.append(permission)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def initialize_default_roles_and_permissions(db: Session):
        # Create default permissions
        permissions = {
            "create_product": "Can create new products",
            "read_product": "Can view products",
            "update_product": "Can update products",
            "delete_product": "Can delete products",
            # Add user management permissions
            "create_user": "Can create new users",
            "read_user": "Can view users",
            "update_user": "Can update users",
            "delete_user": "Can delete users",
            "manage_roles": "Can manage user roles and permissions",
            # Add table management permission
            "manage_tables": "Can manage database tables"
        }

        created_permissions = {}
        for name, description in permissions.items():
            permission = RoleService.get_permission_by_name(db, name)
            if not permission:
                permission = RoleService.create_permission(db, name, description)
            created_permissions[name] = permission

        # Create default roles
        roles = {
            "admin": "Administrator with full access",
            "manager": "Manager with product management access",
            "user": "Regular user with limited access"
        }

        for name, description in roles.items():
            role = RoleService.get_role_by_name(db, name)
            if not role:
                role = RoleService.create_role(db, name, description)

            # Assign permissions based on role
            if name == "admin":
                for permission in created_permissions.values():
                    if permission not in role.permissions:
                        RoleService.add_permission_to_role(db, role, permission)
            elif name == "manager":
                manager_permissions = [
                    "create_product", "read_product", "update_product",
                    "read_user"  # Managers can view users
                ]
                for perm_name in manager_permissions:
                    if created_permissions[perm_name] not in role.permissions:
                        RoleService.add_permission_to_role(db, role, created_permissions[perm_name])
            elif name == "user":
                if created_permissions["read_product"] not in role.permissions:
                    RoleService.add_permission_to_role(db, role, created_permissions["read_product"])

    @staticmethod
    def create_tables():
        """Create role and permission tables if they don't exist"""
        Base.metadata.create_all(bind=engine, tables=[Role.__table__, Permission.__table__]) 