"""Tests for the static roles catalog."""

from __future__ import annotations

from raito.plugins.roles.roles import AVAILABLE_ROLES, AVAILABLE_ROLES_BY_SLUG

EXPECTED_SLUGS = {
    "owner",
    "developer",
    "administrator",
    "moderator",
    "manager",
    "sponsor",
    "guest",
    "support",
    "tester",
}


def test_available_roles_count():
    assert len(AVAILABLE_ROLES) == 9


def test_available_roles_slugs():
    slugs = {role.slug for role in AVAILABLE_ROLES}
    assert slugs == EXPECTED_SLUGS


def test_available_roles_by_slug_mapping():
    assert set(AVAILABLE_ROLES_BY_SLUG) == EXPECTED_SLUGS
    for slug, role in AVAILABLE_ROLES_BY_SLUG.items():
        assert role.slug == slug


def test_role_data_have_metadata():
    for role in AVAILABLE_ROLES:
        assert role.name
        assert role.description
        assert role.emoji
        assert role.label == f"{role.emoji} {role.name}"


def test_rt_exports_role_constraints():
    from raito import rt
    from raito.plugins.roles.constraint import RoleConstraint

    for name in EXPECTED_SLUGS:
        constraint = getattr(rt, name.upper())
        assert isinstance(constraint, RoleConstraint)
        assert constraint.filter.data.slug == name
