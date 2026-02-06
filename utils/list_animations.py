#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
list_animations.py - Utility to list Pepper's installed animations and tags.

USAGE:
    python list_animations.py --ip 127.0.0.1 --port 9559
    python list_animations.py --ip 192.168.0.135 --show-tags
    python list_animations.py --tag Hello
"""

import argparse
import sys

import qi

# Import animation utilities
import os
import sys

# Add package root to path for standalone execution
PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))
if PACKAGE_ROOT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT)

from animations import (
    build_animation_catalog,
    fetch_animation_paths,
    fetch_animation_tags,
    fetch_tag_map,
    debug_player_methods,
)


def connect_session(ip, port):
    session = qi.Session()
    try:
        session.connect("tcp://{}:{}".format(ip, port))
        return session
    except RuntimeError as err:
        print("Failed to connect to NAOqi at {}:{} -- {}".format(ip, port, err))
        return None


def _print_fetch_errors(errors):
    if not errors:
        return
    print("Unable to retrieve animation list via ALAnimationPlayer:")
    for entry in errors:
        for line in entry.splitlines():
            print("  {}".format(line))


def print_animations(session, player, categorize=False, depth=None):
    try:
        if categorize:
            catalog, fetch_result = build_animation_catalog(
                session, depth=depth, player=player
            )
        else:
            fetch_result = fetch_animation_paths(session, player)
            catalog = None
    except RuntimeError as err:
        print("\n{}".format(err))
        return None

    if fetch_result.source != "ALAnimationPlayer" and fetch_result.errors:
        _print_fetch_errors(fetch_result.errors)
        heading = "Animations discovered via {} ({} total):".format(
            fetch_result.source,
            len(fetch_result.animations)
        )
    else:
        heading = "Installed Animations ({} total):".format(
            len(fetch_result.animations)
        )

    print("\n{}".format(heading))

    if categorize and catalog:
        for category, items in catalog.items():
            print("\n[{}] ({} items)".format(category, len(items)))
            for name in items:
                print("  {}".format(name))
    else:
        for name in fetch_result.animations:
            print("  {}".format(name))

    return fetch_result


def print_tags(session, player):
    tag_result = fetch_animation_tags(session, player)

    if not tag_result.tags:
        print("\nNo animation tags found.")
        if tag_result.errors:
            print("Details:")
            for entry in tag_result.errors:
                for line in entry.splitlines():
                    print("  {}".format(line))
        return tag_result

    print("\nAvailable Tags ({} total):".format(len(tag_result.tags)))
    for tag in tag_result.tags:
        print("  {}".format(tag))

    if tag_result.errors:
        print("\nNote: encountered issues while retrieving tags:")
        for entry in tag_result.errors:
            for line in entry.splitlines():
                print("  {}".format(line))

    return tag_result


def print_tag_details(session, player, tag_name):
    mapping, errors = fetch_tag_map(session, tags=[tag_name], player=player)
    animations = mapping.get(tag_name, [])

    if not animations:
        print("No animations found for tag '{}'.".format(tag_name))
        if errors:
            print("Details:")
            for entry in errors:
                for line in entry.splitlines():
                    print("  {}".format(line))
        return

    print("\nAnimations for tag '{}':".format(tag_name))
    for name in animations:
        print("  {}".format(name))


def print_tag_map(session, player, tags=None):
    mapping, errors = fetch_tag_map(session, tags=tags, player=player)
    if not mapping:
        print("\nNo tag-to-animation mappings available.")
        if errors:
            print("Details:")
            for entry in errors:
                for line in entry.splitlines():
                    print("  {}".format(line))
        return

    print("\nTag Map:")
    for tag in sorted(mapping.keys()):
        entries = mapping[tag]
        print("  {} ({} animations)".format(tag, len(entries)))
        for name in entries:
            print("    - {}".format(name))

    if errors:
        print("\nNote: encountered issues while retrieving mappings:")
        for entry in errors:
            for line in entry.splitlines():
                print("  {}".format(line))


def main():
    parser = argparse.ArgumentParser(description="List Pepper animations and tags.")
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Pepper NAOqi IP (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9559,
                        help="Pepper NAOqi port (default: 9559)")
    parser.add_argument("--show-tags", action="store_true",
                        help="Print available animation tags")
    parser.add_argument("--tag", type=str,
                        help="Print all animations tied to the specified tag")
    parser.add_argument("--tag-map", action="store_true",
                        help="Print tag-to-animation mappings")
    parser.add_argument("--by-category", action="store_true",
                        help="Group animations by category")
    parser.add_argument("--category-depth", type=int, default=None,
                        help="Limit category depth when grouping animations")
    parser.add_argument("--debug", action="store_true",
                        help="Print debugging information about the ALAnimationPlayer service")
    args = parser.parse_args()

    session = connect_session(args.ip, args.port)
    if not session:
        sys.exit(1)

    try:
        player = session.service("ALAnimationPlayer")
    except Exception as err:
        print("Unable to obtain ALAnimationPlayer service: {}".format(err))
        sys.exit(1)

    if args.debug:
        debug_player_methods(player)

    print_animations(
        session,
        player,
        categorize=args.by_category,
        depth=args.category_depth
    )

    tag_result = None
    if args.show_tags or args.tag or args.tag_map:
        tag_result = print_tags(session, player)

    if args.tag:
        print_tag_details(session, player, args.tag)

    if args.tag_map:
        tags = tag_result.tags if tag_result else None
        print_tag_map(session, player, tags=tags)


if __name__ == "__main__":
    main()
