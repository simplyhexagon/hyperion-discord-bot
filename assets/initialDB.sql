-- Hyperion Discord Bot Initial Database

CREATE TABLE IF NOT EXISTS `inventory`(
    uid VARCHAR(18),
    invitem VARCHAR(30),
    itemcount INTEGER(5)
);

--A

CREATE TABLE IF NOT EXISTS `levels`(
    uid VARCHAR(18),
    xp INTEGER,
    userlevel INTEGER
);