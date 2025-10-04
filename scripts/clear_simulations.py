#!/usr/bin/env python3
"""
Script to clear all simulations from the memory backend.

This script removes all simulations, actors, events, and actions
from the local state store used by the memory backend.
"""

import asyncio
from pathlib import Path

# Add the src directory to the path so we can import scrai modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scrai.cli.store import LocalStateStore, DEFAULT_STATE_PATH


def clear_all_data():
    """Clear all data from the local state store."""
    print("🧹 Clearing all simulation data...")

    # Use the default state path
    store = LocalStateStore(DEFAULT_STATE_PATH)

    # Clear all collections
    collections = ["simulations", "actors", "events", "actions"]

    for collection in collections:
        items = store.collection_items(collection)
        if items:
            print(f"  Removing {len(items)} items from {collection}")
            store.bulk_put(collection, {})
        else:
            print(f"  No items found in {collection}")

    print("✅ All simulation data cleared!")
    print(f"📁 State file: {DEFAULT_STATE_PATH}")


def show_current_data():
    """Show current data before clearing (optional)."""
    print("📊 Current state:")

    store = LocalStateStore(DEFAULT_STATE_PATH)

    for collection in ["simulations", "actors", "events", "actions"]:
        items = store.collection_items(collection)
        print(f"  {collection}: {len(items)} items")

    print()


if __name__ == "__main__":
    print("ScrAI Memory Store Cleanup")
    print("=" * 40)

    # Show current data
    show_current_data()

    # Ask for confirmation
    confirm = input("⚠️  This will delete ALL simulation data. Continue? (y/N): ").lower().strip()

    if confirm in ['y', 'yes']:
        clear_all_data()
        print("\n🎉 Cleanup complete! You can now start fresh.")
    else:
        print("\n❌ Operation cancelled.")
