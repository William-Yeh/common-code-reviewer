# Test sample #2: User management — targets general SKILL.md principles
# Focuses on: OCP, LSP, ISP, Testability, Clean Code, Architecture, FP, Security

import os
import json
import subprocess
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path


# ─── ISP: Fat abstract base class ───────────────────────────────────
# [ISSUE: ISP violation — forces all implementations to define 8 methods]
class IUserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: str) -> dict: ...
    @abstractmethod
    def find_by_email(self, email: str) -> dict: ...
    @abstractmethod
    def save(self, user: dict) -> None: ...
    @abstractmethod
    def delete(self, user_id: str) -> None: ...
    @abstractmethod
    def bulk_import(self, users: list[dict]) -> int: ...
    @abstractmethod
    def export_csv(self) -> str: ...
    @abstractmethod
    def generate_report(self) -> dict: ...
    @abstractmethod
    def archive_inactive(self, days: int) -> int: ...


# ─── LSP: Subtype contract violation ────────────────────────────────
class BaseDiscount:
    """Contract: calculate() returns a float between 0.0 and 1.0 (0% to 100% discount)."""

    def calculate(self, order_total: float) -> float:
        return 0.0  # no discount by default


class PremiumDiscount(BaseDiscount):
    def calculate(self, order_total: float) -> float:
        return 0.15  # 15% discount


# [ISSUE: LSP violation — returns value > 1.0, violating base class contract]
class EmployeeDiscount(BaseDiscount):
    def calculate(self, order_total: float) -> float:
        # Returns absolute dollar amount instead of a fraction — breaks callers using `total * (1 - discount)`
        return 50.0


# ─── OCP: if/elif chain that must grow ──────────────────────────────
# [ISSUE: OCP violation — every new role requires modifying this function]
def get_permissions(role: str) -> list[str]:
    if role == "admin":
        return ["read", "write", "delete", "manage_users", "view_audit"]
    elif role == "editor":
        return ["read", "write"]
    elif role == "viewer":
        return ["read"]
    elif role == "moderator":
        return ["read", "write", "delete"]
    elif role == "analyst":
        return ["read", "view_audit"]
    # [ISSUE: No else clause — returns None implicitly for unknown roles]
    # Should raise an error or return empty list explicitly


# ─── Architecture: Anemic domain model ──────────────────────────────
# [ISSUE: Pure data class — all logic lives in service functions below]
class User:
    def __init__(self, id: str, name: str, email: str, role: str, status: str):
        self.id = id
        self.name = name
        self.email = email
        self.role = role       # [ISSUE: str instead of Literal/Enum]
        self.status = status   # [ISSUE: str instead of Literal/Enum]
        self.created_at = None
        self.last_login = None


# ─── FP: Hidden side effects ────────────────────────────────────────
# [ISSUE: Named "validate" but has side effects — writes to filesystem and sends HTTP]
def validate_user_data(data: dict) -> bool:
    is_valid = (
        "email" in data
        and "@" in data["email"]
        and "name" in data
        and len(data["name"]) > 0
    )

    # [ISSUE: Side effect hidden in validation function]
    with open("/var/log/validation.log", "a") as f:
        f.write(f"{datetime.now()}: validated {data.get('email')} -> {is_valid}\n")

    # [ISSUE: Another hidden side effect — HTTP call from a "validate" function]
    import requests
    requests.post("https://analytics.internal/track", json={"event": "validation", "valid": is_valid})

    return is_valid


# ─── Testability ─────────────────────────────────────────────────────
class UserService:
    # [ISSUE: Hard-coded dependency — directly reads filesystem, not injectable]
    def load_config(self) -> dict:
        return json.loads(Path("/etc/app/config.json").read_text())

    # [ISSUE: Non-deterministic — uses datetime.now() directly]
    def deactivate_inactive_users(self, users: list[User], threshold_days: int) -> list[User]:
        deactivated = []
        for user in users:
            if user.last_login:
                # [ISSUE: Deep nesting starts here — 3+ levels]
                days_inactive = (datetime.now() - user.last_login).days
                if days_inactive > threshold_days:
                    if user.status != "admin":
                        if user.status != "protected":
                            user.status = "inactive"
                            deactivated.append(user)
        return deactivated

    # [ISSUE: Mixed abstraction levels — config loading, business logic, file I/O, all in one]
    def generate_user_report(self, users: list[User]) -> str:
        config = self.load_config()
        report_dir = config.get("report_dir", "/tmp")

        # [ISSUE: Code duplication — same role-counting logic used elsewhere]
        admin_count = 0
        editor_count = 0
        viewer_count = 0
        for user in users:
            if user.role == "admin":
                admin_count += 1
            elif user.role == "editor":
                editor_count += 1
            elif user.role == "viewer":
                viewer_count += 1

        report = f"Admins: {admin_count}, Editors: {editor_count}, Viewers: {viewer_count}"

        # [ISSUE: Side effect in report generation — writes file]
        path = os.path.join(report_dir, f"report_{datetime.now().strftime('%Y%m%d')}.txt")
        with open(path, "w") as f:
            f.write(report)

        return report


# ─── Clean Code: Bad naming + dead code ──────────────────────────────
# [ISSUE: Bad naming — what are d, tmp, x, flag?]
def proc(d, flag=False):
    tmp = []
    for x in d:
        if flag:
            tmp.append(x)
        else:
            # [ISSUE: Duplicated email validation — same check as validate_user_data]
            if x.get("email") and "@" in x["email"]:
                tmp.append(x)
    return tmp


# [ISSUE: Dead code — never called]
def _old_send_welcome_email(email: str, name: str):
    """Deprecated: replaced by notification service."""
    import smtplib
    server = smtplib.SMTP("mail.internal", 587)
    server.sendmail("noreply@example.com", email, f"Welcome {name}")
    server.quit()


# ─── Security ────────────────────────────────────────────────────────
# [ISSUE: Command injection — user input passed to subprocess without sanitization]
def export_user_data(username: str, output_format: str) -> str:
    result = subprocess.run(
        f"user-export --user {username} --format {output_format}",
        shell=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


# [ISSUE: Path traversal — user-controlled filename without sanitization]
def get_user_avatar(user_id: str) -> bytes:
    # User could pass "../../etc/passwd" as user_id
    avatar_path = f"/var/data/avatars/{user_id}.png"
    with open(avatar_path, "rb") as f:
        return f.read()


# [ISSUE: No authorization check — any authenticated user can delete any other user]
def delete_user(requesting_user: User, target_user_id: str, repo: IUserRepository) -> None:
    # Should verify requesting_user has permission to delete target_user_id
    repo.delete(target_user_id)
