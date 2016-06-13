from uuid import UUID


def is_uuid4(uuid_string):
    """
    Validate that a UUID string is in
    fact a valid uuid4.
    """
    try:
        UUID(uuid_string, version=4)
    except (ValueError, TypeError):
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        # None will raise TypeError.
        return False
    return True


def compute_cia(insee, fantoir, number=None, ordinal=None):
    return '_'.join([insee, fantoir, (number or '').upper(),
                     (ordinal or '').upper()])


def make_diff(old, new, update=False):
    """Create a diff between two versions of the same resource.

    update      only consider new keys"""
    meta = set(['pk', 'id', 'created_by', 'modified_by', 'created_at',
                'modified_at', 'version', 'cia'])
    keys = list(new)
    if not update:
        keys += list(old)
    keys = set(keys) - meta
    diff = {}
    for key in keys:
        old_value = old.get(key)
        new_value = new.get(key)
        if new_value != old_value:
            diff[key] = {
                'old': str(old_value),
                'new': str(new_value)
            }
    return diff
