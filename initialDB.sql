-- Hyperion Discord Bot Initial Database

CREATE TABLE IF NOT EXISTS `inventory`(
    uid VARCHAR(20),
    invitem VARCHAR(20),
    itemcount INTEGER(5)
);