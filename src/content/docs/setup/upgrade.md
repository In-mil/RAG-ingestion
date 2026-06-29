# Upgrade Guide

## Before You Start

- Back up your database
- Note your current version number
- Review the changelog for breaking changes

## Steps

1. Stop the running service
2. Pull the latest release
3. Run `pip install -r requirements.txt` to update dependencies
4. Apply database migrations with `python migrate.py`
5. Restart the service

## Rolling Back

If something goes wrong, restore the database backup and revert to the previous release.
