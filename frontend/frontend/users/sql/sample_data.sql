-- insert some data
INSERT INTO users(id, login, passwd, is_superuser, disabled)
VALUES (1, 'admin', 'admin1', TRUE, FALSE);
INSERT INTO users(id, login, passwd, is_superuser, disabled)
VALUES (2, 'moderator', 'moderator2', FALSE, FALSE);
INSERT INTO users(id, login, passwd, is_superuser, disabled)
VALUES (3, 'user', 'user3', FALSE, FALSE);

INSERT INTO permissions(id, user_id, perm_name)
VALUES (1, 2, 'protected');
INSERT INTO permissions(id, user_id, perm_name)
VALUES (2, 2, 'public');
INSERT INTO permissions(id, user_id, perm_name)
VALUES (3, 3, 'public');
