# -*- coding: utf-8 -*-
"""One-time script to create missing users tables on an existing database."""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

import django

django.setup()

from django.db import connection

cursor = connection.cursor()


def sql(sql_str, label=""):
    try:
        cursor.execute(sql_str)
        print(f"  OK: {label or sql_str[:80]}")
    except Exception as e:
        print(f"  SKIP: {label or sql_str[:60]} — {e}")


# 1. Add new columns to existing users_user table
print("\n=== Adding columns to users_user ===")
sql("ALTER TABLE users_user ADD COLUMN leader_id bigint NULL", "leader_id")
sql("ALTER TABLE users_user ADD COLUMN department_id bigint NULL", "department_id")

# 2. Create new tables
print("\n=== Creating new tables ===")

tables = {
    "users_department": """CREATE TABLE users_department (
        id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
        name varchar(255) NOT NULL,
        parent_id bigint NULL,
        lft integer UNSIGNED NOT NULL CHECK (lft >= 0),
        rght integer UNSIGNED NOT NULL CHECK (rght >= 0),
        tree_id integer UNSIGNED NOT NULL CHECK (tree_id >= 0),
        level integer UNSIGNED NOT NULL CHECK (level >= 0),
        `order` integer NOT NULL DEFAULT 0,
        is_active bool NOT NULL DEFAULT TRUE
    )""",
    "users_permission": """CREATE TABLE users_permission (
        id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
        code varchar(128) NOT NULL UNIQUE,
        name varchar(255) NOT NULL,
        category varchar(64) NOT NULL,
        permission_type varchar(16) NOT NULL,
        description longtext NOT NULL,
        is_builtin bool NOT NULL DEFAULT FALSE
    )""",
    "users_security_policy": """CREATE TABLE users_security_policy (
        id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
        `key` varchar(128) NOT NULL UNIQUE,
        value json NOT NULL,
        category varchar(32) NOT NULL,
        description longtext NOT NULL,
        is_builtin bool NOT NULL DEFAULT TRUE
    )""",
    "users_login_attempt": """CREATE TABLE users_login_attempt (
        id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
        username varchar(128) NOT NULL,
        ip_address char(39) NOT NULL,
        attempts integer NOT NULL DEFAULT 0,
        locked_until datetime(6) NULL,
        UNIQUE(username, ip_address)
    )""",
    "users_password_history": """CREATE TABLE users_password_history (
        id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
        password_hash varchar(255) NOT NULL,
        created_at datetime(6) NOT NULL,
        user_id bigint NOT NULL
    )""",
    "users_role": """CREATE TABLE users_role (
        id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
        name varchar(255) NOT NULL,
        role_key varchar(128) NOT NULL UNIQUE,
        `desc` longtext NOT NULL,
        is_builtin bool NOT NULL DEFAULT FALSE,
        creator varchar(128) NOT NULL DEFAULT '',
        create_at datetime(6) NOT NULL,
        update_at datetime(6) NOT NULL,
        updated_by varchar(128) NOT NULL DEFAULT '',
        is_deleted bool NOT NULL DEFAULT FALSE,
        end_at datetime(6) NULL
    )""",
    "users_user_group": """CREATE TABLE users_user_group (
        id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
        name varchar(255) NOT NULL,
        group_key varchar(128) NOT NULL UNIQUE,
        `desc` longtext NOT NULL,
        is_builtin bool NOT NULL DEFAULT FALSE,
        project_key varchar(64) NOT NULL DEFAULT '0',
        creator varchar(128) NOT NULL DEFAULT '',
        create_at datetime(6) NOT NULL,
        update_at datetime(6) NOT NULL,
        updated_by varchar(128) NOT NULL DEFAULT '',
        is_deleted bool NOT NULL DEFAULT FALSE,
        end_at datetime(6) NULL
    )""",
    "users_dept_membership": """CREATE TABLE users_dept_membership (
        id bigint AUTO_INCREMENT NOT NULL PRIMARY KEY,
        is_primary bool NOT NULL DEFAULT FALSE,
        department_id bigint NOT NULL,
        user_id bigint NOT NULL,
        UNIQUE(user_id, department_id)
    )""",
    "users_role_members": """CREATE TABLE users_role_members (
        id integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        role_id bigint NOT NULL,
        user_id bigint NOT NULL,
        UNIQUE(role_id, user_id)
    )""",
    "users_role_owners": """CREATE TABLE users_role_owners (
        id integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        role_id bigint NOT NULL,
        user_id bigint NOT NULL,
        UNIQUE(role_id, user_id)
    )""",
    "users_role_permissions": """CREATE TABLE users_role_permissions (
        id integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        role_id bigint NOT NULL,
        permission_id bigint NOT NULL,
        UNIQUE(role_id, permission_id)
    )""",
    "users_user_group_members": """CREATE TABLE users_user_group_members (
        id integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        usergroup_id bigint NOT NULL,
        user_id bigint NOT NULL,
        UNIQUE(usergroup_id, user_id)
    )""",
    "users_user_group_owners": """CREATE TABLE users_user_group_owners (
        id integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
        usergroup_id bigint NOT NULL,
        user_id bigint NOT NULL,
        UNIQUE(usergroup_id, user_id)
    )""",
}

for table, ddl in tables.items():
    try:
        cursor.execute(f"SELECT 1 FROM {table} LIMIT 1")
        print(f"  EXISTS: {table}")
    except Exception:
        cursor.execute(ddl)
        print(f"  CREATED: {table}")

# 3. Add foreign keys and indexes
print("\n=== Adding FK constraints and indexes ===")
constraints = [
    ("ALTER TABLE users_department ADD CONSTRAINT users_dept_parent_fk "
     "FOREIGN KEY (parent_id) REFERENCES users_department(id)"),
    ("ALTER TABLE users_user ADD CONSTRAINT users_user_leader_fk "
     "FOREIGN KEY (leader_id) REFERENCES users_user(id)"),
    ("ALTER TABLE users_user ADD CONSTRAINT users_user_dept_fk "
     "FOREIGN KEY (department_id) REFERENCES users_department(id)"),
    "CREATE INDEX users_dept_parent_idx ON users_department(parent_id)",
    "CREATE INDEX users_dept_tree_idx ON users_department(tree_id)",
    "CREATE INDEX users_la_username_idx ON users_login_attempt(username)",
    ("ALTER TABLE users_password_history ADD CONSTRAINT users_ph_user_fk "
     "FOREIGN KEY (user_id) REFERENCES users_user(id)"),
    ("ALTER TABLE users_dept_membership ADD CONSTRAINT users_dm_dept_fk "
     "FOREIGN KEY (department_id) REFERENCES users_department(id)"),
    ("ALTER TABLE users_dept_membership ADD CONSTRAINT users_dm_user_fk "
     "FOREIGN KEY (user_id) REFERENCES users_user(id)"),
    ("ALTER TABLE users_role_members ADD CONSTRAINT users_rm_role_fk "
     "FOREIGN KEY (role_id) REFERENCES users_role(id)"),
    ("ALTER TABLE users_role_members ADD CONSTRAINT users_rm_user_fk "
     "FOREIGN KEY (user_id) REFERENCES users_user(id)"),
    ("ALTER TABLE users_role_owners ADD CONSTRAINT users_ro_role_fk "
     "FOREIGN KEY (role_id) REFERENCES users_role(id)"),
    ("ALTER TABLE users_role_owners ADD CONSTRAINT users_ro_user_fk "
     "FOREIGN KEY (user_id) REFERENCES users_user(id)"),
    ("ALTER TABLE users_role_permissions ADD CONSTRAINT users_rp_role_fk "
     "FOREIGN KEY (role_id) REFERENCES users_role(id)"),
    ("ALTER TABLE users_role_permissions ADD CONSTRAINT users_rp_perm_fk "
     "FOREIGN KEY (permission_id) REFERENCES users_permission(id)"),
    ("ALTER TABLE users_user_group_members ADD CONSTRAINT users_ugm_group_fk "
     "FOREIGN KEY (usergroup_id) REFERENCES users_user_group(id)"),
    ("ALTER TABLE users_user_group_members ADD CONSTRAINT users_ugm_user_fk "
     "FOREIGN KEY (user_id) REFERENCES users_user(id)"),
    ("ALTER TABLE users_user_group_owners ADD CONSTRAINT users_ugo_group_fk "
     "FOREIGN KEY (usergroup_id) REFERENCES users_user_group(id)"),
    ("ALTER TABLE users_user_group_owners ADD CONSTRAINT users_ugo_user_fk "
     "FOREIGN KEY (user_id) REFERENCES users_user(id)"),
]

for c in constraints:
    label = c.split("ADD CONSTRAINT ")[-1].split(" ")[0] if "CONSTRAINT" in c else c[:60]
    sql(c, label)

# 4. Mark migration as applied
print("\n=== Marking migration as applied ===")
sql(
    "INSERT IGNORE INTO django_migrations (app, name, applied) "
    "VALUES ('users', '0001_initial', NOW())",
    "users.0001_initial",
)

print("\nDone! All users tables created.")
