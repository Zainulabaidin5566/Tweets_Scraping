CREATE VIEW users_view 
AS 
SELECT Tag, GROUP_CONCAT(username, ',') AS `usernames`
FROM users
GROUP BY Tag