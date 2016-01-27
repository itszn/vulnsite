CREATE TABLE IF NOT EXISTS `user` (
    `id` INTEGER NOT NULL,
    `name` TEXT NOT NULL,
    `salt` VARCHAR(16) DEFAULT NULL,
    `pass` VARCHAR(64) DEFAULT NULL,
    `points` INTEGER NOT NULL DEFAULT 0,
    `permission` INTEGER NOT NULL DEFAULT 0,

    `numNots` INTEGER NOT NULL DEFAULT 0,
    `sentLink` INTEGER NOT NULL DEFAULT 0,

    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `post` (
    `id` INTEGER NOT NULL,
    `user` INTEGER NOT NULL,
    `title` TEXT NOT NULL,
    `body` TEXT NOT NULL,
    `points` INTEGER NOT NULL DEFAULT 0,
    `numComments` INTEGER NOT NULL DEFAULT 0,
    `time` INTEGER NOT NULL DEFAULT 0,
    `permission` INTEGER NOT NULL DEFAULT 0,

    `userName` TEXT NOT NULL,

    PRIMARY KEY (`id`),
    FOREIGN KEY (`user`) REFERENCES `user`(`id`)
);

CREATE TABLE IF NOT EXISTS `vote` (
    `id` INTEGER NOT NULL,
    `user` INTEGER NOT NULL,
    `post` INTEGER NOT NULL DEFAULT 0,
    `comment` INTEGER NOT NULL DEFAULT 0,
    `way` INTEGER NOT NULL,

    PRIMARY KEY(`id`),
    FOREIGN KEY (`user`) REFERENCES `user`(`id`),
    FOREIGN KEY (`post`) REFERENCES `user`(`post`)
);

CREATE TABLE IF NOT EXISTS `comment` (
    `id` INTEGER NOT NULL,
    `user` INTEGER NOT NULL,
    `post` INTEGER NOT NULL,
    `body` TEXT NOT NULL,
    `points` INTEGER NOT NULL DEFAULT 0,
    `time` INTEGER NOT NULL DEFAULT 0,

    `userName` TEXT NOT NULL,

    PRIMARY KEY (`id`),
    FOREIGN KEY (`user`) REFERENCES `user`(`id`),
    FOREIGN KEY (`post`) REFERENCES `user`(`post`)
);

CREATE TABLE IF NOT EXISTS `message` (
    `id` INTEGER NOT NULL,
    `to` INTEGER NOT NULL,
    `from` INTEGER NOT NULL,
    `body` TEXT NOT NULL,
    `time` INTEGER NOT NULL DEFAULT 0,

    `raw` INTEGER NOT NULL DEFAULT 0,

    `fromName` TEXT NOT NULL,

    PRIMARY KEY (`id`),
    FOREIGN KEY (`to`) REFERENCES `user`(`id`),
    FOREIGN KEY (`from`) REFERENCES `user`(`id`)
);

