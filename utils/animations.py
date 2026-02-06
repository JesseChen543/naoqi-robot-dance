# -*- coding: utf-8 -*-

"""
Utilities for discovering and categorizing Pepper's stock animations.

The helpers in this module consolidate the logic for querying NAOqi's
ALAnimationPlayer service (with graceful fallbacks to ALBehaviorManager)
and expose structured catalogs that can be consumed by UIs or CLI tools.
"""

from collections import defaultdict, namedtuple, OrderedDict

try:  # Python 2 / 3 compatibility
    basestring  # noqa: F821 pylint: disable=undefined-variable
except NameError:  # pragma: no cover
    basestring = str  # noqa: A001

FetchResult = namedtuple("FetchResult", ["animations", "source", "errors"])
TagResult = namedtuple("TagResult", ["tags", "errors"])


def _normalize_arg_options(arg_options):
    if not arg_options:
        return [tuple()]

    normalized = []
    for option in arg_options:
        if isinstance(option, tuple):
            normalized.append(option)
        elif isinstance(option, list):
            normalized.append(tuple(option))
        else:
            normalized.append((option,))
    return normalized


def _invoke_player_method(player, method_names, arg_options=None):
    """
    Call a method on ALAnimationPlayer, falling back to the generic
    qi.AnyObject call interface when stubs are not exposed.
    """
    if isinstance(method_names, basestring):
        method_names = [method_names]

    arg_options = _normalize_arg_options(arg_options)
    errors = []

    for method_name in method_names:
        method = getattr(player, method_name, None)
        if callable(method):
            for args in arg_options:
                try:
                    return method(*args)
                except TypeError as err:
                    errors.append("{}{} -> {}".format(method_name, args, err))
                except RuntimeError as err:
                    errors.append("{}{} -> {}".format(method_name, args, err))

        call_method = getattr(player, "call", None)
        if callable(call_method):
            for args in arg_options:
                try:
                    return call_method(method_name, *args)
                except RuntimeError as err:
                    errors.append("{}{} -> {}".format(method_name, args, err))

    details = "\n  ".join(errors) if errors else "  <no candidates attempted>"

    available = []
    try:
        meta_obj = player.metaObject()
        available = [method.name() for method in meta_obj.methods()]
    except Exception:
        pass

    raise AttributeError(
        "ALAnimationPlayer service does not expose expected methods:\n"
        "  {}\nAttempts:\n  {}\nAvailable methods (best effort):\n  {}".format(
            ", ".join(method_names),
            details,
            ", ".join(sorted(available)) if available else "<unknown>"
        )
    )


def discover_behavior_animations(session):
    """
    Attempt to discover animation names via ALBehaviorManager as a fallback.
    """
    if not session:
        return []

    try:
        behavior_manager = session.service("ALBehaviorManager")
    except Exception:
        return []

    try:
        behaviors = behavior_manager.getInstalledBehaviors()
    except Exception:
        return []

    return sorted(
        behavior for behavior in behaviors
        if behavior.startswith("animations/")
    )


def fetch_animation_paths(session, player=None):
    """
    Retrieve available animation paths, falling back to ALBehaviorManager when
    ALAnimationPlayer does not expose list APIs.
    """
    errors = []

    if player is None:
        try:
            player = session.service("ALAnimationPlayer")
        except Exception as err:
            raise RuntimeError("Unable to obtain ALAnimationPlayer: {}".format(err))

    try:
        animations = sorted(
            _invoke_player_method(
                player,
                [
                    "getInstalledAnimations",
                    "getAvailableAnimations",
                    "getAnimationList",
                    "installedAnimations",
                ],
                arg_options=[tuple(), (False,), (True,)]
            )
        )
        return FetchResult(animations, "ALAnimationPlayer", errors)
    except AttributeError as err:
        errors.append(str(err))

    fallback = discover_behavior_animations(session)
    if fallback:
        return FetchResult(fallback, "ALBehaviorManager", errors)

    raise RuntimeError(
        "Unable to retrieve Pepper animations via ALAnimationPlayer or "
        "ALBehaviorManager. Errors: {}".format("; ".join(errors))
    )


def fetch_animation_tags(session, player=None):
    """
    Retrieve animation tags provided by ALAnimationPlayer.
    """
    errors = []

    if player is None:
        try:
            player = session.service("ALAnimationPlayer")
        except Exception as err:
            raise RuntimeError("Unable to obtain ALAnimationPlayer: {}".format(err))

    try:
        tags = sorted(
            _invoke_player_method(
                player,
                ["getTagList", "getAnimationTags", "tagList"],
                arg_options=[tuple(), (False,), (True,)]
            )
        )
        return TagResult(tags, errors)
    except AttributeError as err:
        errors.append(str(err))

    return TagResult([], errors)


def fetch_tag_map(session, tags=None, player=None):
    """
    Retrieve a mapping of tag -> animation paths.
    """
    if player is None:
        try:
            player = session.service("ALAnimationPlayer")
        except Exception as err:
            raise RuntimeError("Unable to obtain ALAnimationPlayer: {}".format(err))

    tag_result = fetch_animation_tags(session, player)
    tag_names = tags if tags is not None else tag_result.tags

    mapping = {}
    for tag_name in tag_names:
        try:
            animations = sorted(
                _invoke_player_method(
                    player,
                    ["getAnimationsTag", "getAnimationsForTag"],
                    arg_options=[(tag_name,), (tag_name, False), (tag_name, True)]
                )
            )
        except Exception:
            animations = []

        if animations:
            mapping[tag_name] = animations

    return mapping, tag_result.errors


def categorize_paths(paths, depth=None):
    """
    Group animation paths by their directory segments.

    Args:
        paths: list[str] - animation paths (e.g., animations/Stand/Gestures/Hey_1)
        depth: int or None - number of segments (excluding the 'animations'
            prefix and terminal animation name) to include in the category.

    Returns:
        OrderedDict[str, list[str]] mapping category -> sorted paths.
    """
    categories = defaultdict(list)

    for path in paths:
        if not isinstance(path, basestring):
            continue

        normalized = path.strip()
        if not normalized:
            continue

        if normalized.startswith("animations/"):
            parts = normalized.split("/")
            if len(parts) <= 2:
                category_segments = parts[1:-1]
            else:
                segment_slice = parts[1:-1]
                if depth is not None and depth > 0:
                    segment_slice = segment_slice[:depth]
                category_segments = segment_slice
        else:
            category_segments = ["Custom"]

        category = " / ".join(category_segments) if category_segments else "General"
        categories[category].append(normalized)

    ordered = OrderedDict()
    for category in sorted(categories.keys()):
        ordered[category] = sorted(categories[category])

    return ordered


def build_animation_catalog(session, depth=None, player=None):
    """
    Fetch animations and return a categorized catalog.

    Returns:
        (catalog, fetch_result) where catalog is an OrderedDict.
    """
    fetch_result = fetch_animation_paths(session, player)
    catalog = categorize_paths(fetch_result.animations, depth=depth)
    return catalog, fetch_result


def debug_player_methods(player):
    """Print available methods on the ALAnimationPlayer proxy for debugging."""
    print("\n[debug] Introspecting ALAnimationPlayer service...")

    try:
        meta = player.metaObject()
        method_names = sorted(method.name() for method in meta.methods())
        print("  metaObject methods ({}):".format(len(method_names)))
        for name in method_names:
            print("    - {}".format(name))
    except Exception as err:
        print("  Unable to retrieve metaObject methods: {}".format(err))

    try:
        attrs = sorted(
            name for name in dir(player)
            if not name.startswith("_")
        )
        print("  dir(player) attributes ({}):".format(len(attrs)))
        for name in attrs:
            print("    - {}".format(name))
    except Exception as err:
        print("  Unable to list attributes via dir(): {}".format(err))
