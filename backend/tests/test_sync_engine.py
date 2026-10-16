"""Tests for the sync engine."""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from app.services.sync_engine import calculate_desired_state, calculate_diff


def test_basic_role_grant():
    """Test basic role-based library grant."""
    user_roles = ["role1"]
    role_library_map = {"role1": {1, 2}}
    manual_grants = set()
    current_libraries = set()
    exempt_libraries = set()

    desired = calculate_desired_state(
        user_roles, role_library_map, manual_grants, current_libraries, exempt_libraries
    )
    assert desired == {1, 2}


def test_multiple_roles_union():
    """Test that multiple roles grant union of libraries."""
    user_roles = ["role1", "role2"]
    role_library_map = {"role1": {1}, "role2": {2}}
    manual_grants = set()
    current_libraries = set()
    exempt_libraries = set()

    desired = calculate_desired_state(
        user_roles, role_library_map, manual_grants, current_libraries, exempt_libraries
    )
    assert desired == {1, 2}


def test_role_removed_library_stays():
    """Test that library stays when one of two granting roles is removed."""
    user_roles = ["role1"]  # role2 removed
    role_library_map = {"role1": {1}, "role2": {1}}
    manual_grants = set()
    current_libraries = {1}
    exempt_libraries = set()

    desired = calculate_desired_state(
        user_roles, role_library_map, manual_grants, current_libraries, exempt_libraries
    )
    assert desired == {1}


def test_manual_grant_preserved():
    """Test that manual grants are preserved when role is removed."""
    user_roles = []  # role removed
    role_library_map = {"role1": {1}}
    manual_grants = {1}
    current_libraries = {1}
    exempt_libraries = set()

    desired = calculate_desired_state(
        user_roles, role_library_map, manual_grants, current_libraries, exempt_libraries
    )
    assert desired == {1}


def test_exempt_library_preserved():
    """Test that exempt libraries are preserved."""
    user_roles = []
    role_library_map = {"role1": {1}}
    manual_grants = set()
    current_libraries = {2}
    exempt_libraries = {2}

    desired = calculate_desired_state(
        user_roles, role_library_map, manual_grants, current_libraries, exempt_libraries
    )
    assert desired == {2}


def test_exempt_library_not_added():
    """Test that exempt libraries are not added by role."""
    user_roles = ["role1"]
    role_library_map = {"role1": {2}}
    manual_grants = set()
    current_libraries = set()
    exempt_libraries = {2}

    desired = calculate_desired_state(
        user_roles, role_library_map, manual_grants, current_libraries, exempt_libraries
    )
    assert desired == set()


def test_calculate_diff_add():
    """Test diff calculation for adding libraries."""
    current = {1}
    desired = {1, 2}
    to_add, to_remove = calculate_diff(current, desired)
    assert to_add == {2}
    assert to_remove == set()


def test_calculate_diff_remove():
    """Test diff calculation for removing libraries."""
    current = {1, 2}
    desired = {1}
    to_add, to_remove = calculate_diff(current, desired)
    assert to_add == set()
    assert to_remove == {2}


def test_calculate_diff_no_change():
    """Test diff calculation when no change needed."""
    current = {1, 2}
    desired = {1, 2}
    to_add, to_remove = calculate_diff(current, desired)
    assert to_add == set()
    assert to_remove == set()