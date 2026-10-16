"""Sync engine: pure desired-state calculator and diff/apply layer."""

from typing import Dict, List, Set, Tuple


def calculate_desired_state(
    user_roles: List[str],
    role_library_map: Dict[str, Set[int]],
    manual_grants: Set[int],
    current_libraries: Set[int],
    exempt_libraries: Set[int],
) -> Set[int]:
    """Calculate the desired set of libraries for a user.

    Args:
        user_roles: List of role IDs the user has.
        role_library_map: Mapping of role ID to set of library keys.
        manual_grants: Set of library keys manually granted to the user.
        current_libraries: Set of library keys currently shared with the user.
        exempt_libraries: Set of library keys that are exempt from sync.

    Returns:
        Set of library keys that should be shared with the user.
    """
    # Calculate role-based libraries (union of all role grants)
    role_libs = set()
    for role_id in user_roles:
        if role_id in role_library_map:
            role_libs.update(role_library_map[role_id])

    # Calculate managed universe (all libraries in any role mapping, minus exempt)
    managed_universe = set()
    for libs in role_library_map.values():
        managed_universe.update(libs)
    managed_universe -= exempt_libraries

    # Calculate desired managed libraries
    desired_managed = (role_libs | manual_grants) & managed_universe

    # Calculate preserved libraries (exempt or not in managed universe)
    preserved = current_libraries & (exempt_libraries | (set() - managed_universe))

    # Calculate target set
    target = desired_managed | preserved | manual_grants

    return target


def calculate_diff(
    current_libraries: Set[int],
    desired_libraries: Set[int],
) -> Tuple[Set[int], Set[int]]:
    """Calculate the diff between current and desired library sets.

    Args:
        current_libraries: Set of library keys currently shared.
        desired_libraries: Set of library keys that should be shared.

    Returns:
        Tuple of (to_add, to_remove) sets.
    """
    to_add = desired_libraries - current_libraries
    to_remove = current_libraries - desired_libraries
    return to_add, to_remove


def apply_sync(
    user,
    current_libraries: Set[int],
    desired_libraries: Set[int],
    plex_gateway,
    dry_run: bool = False,
    logger=None,
) -> Dict:
    """Apply the sync for a user.

    Args:
        user: The Plex user object.
        current_libraries: Set of library keys currently shared.
        desired_libraries: Set of library keys that should be shared.
        plex_gateway: The PlexGateway instance to use for API calls.
        dry_run: If True, don't actually make changes.
        logger: Optional logger instance.

    Returns:
        Dict with sync results.
    """
    to_add, to_remove = calculate_diff(current_libraries, desired_libraries)

    result = {
        "user_id": user.id,
        "user_name": user.username,
        "to_add": list(to_add),
        "to_remove": list(to_remove),
        "changes_made": False,
        "errors": [],
    }

    if not to_add and not to_remove:
        if logger:
            logger.info(f"No changes needed for {user.username}")
        return result

    if dry_run:
        if logger:
            logger.info(f"[DRY RUN] Would add {to_add} and remove {to_remove} for {user.username}")
        return result

    # Apply changes
    try:
        success = plex_gateway.set_user_libraries(user, desired_libraries)
        if success:
            result["changes_made"] = True
            if logger:
                logger.info(f"Synced {user.username}: added {to_add}, removed {to_remove}")
        else:
            result["errors"].append("Failed to set libraries")
            if logger:
                logger.error(f"Failed to sync {user.username}")
    except Exception as e:
        result["errors"].append(str(e))
        if logger:
            logger.error(f"Error syncing {user.username}: {e}")

    return result