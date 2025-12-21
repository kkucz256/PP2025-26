ALTER DATABASE CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(100) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `role` VARCHAR(50) NOT NULL,
  `mail` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_username_unique` (`username`),
  UNIQUE KEY `users_mail_unique` (`mail`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `quiz` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `content` VARCHAR(255) NOT NULL,
  `slug` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `quiz_slug_unique` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `question` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `quiz_id` INT NOT NULL,
  `content` LONGTEXT NOT NULL,
  `position` INT DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `question_quiz_id_fk_quiz_id` (`quiz_id`),
  CONSTRAINT `question_quiz_id_fk_quiz_id` FOREIGN KEY (`quiz_id`) REFERENCES `quiz` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `answers` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `question_id` INT NOT NULL,
  `content` LONGTEXT NOT NULL,
  `is_correct` INT DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `answers_question_id_fk_question_id` (`question_id`),
  CONSTRAINT `answers_question_id_fk_question_id` FOREIGN KEY (`question_id`) REFERENCES `question` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `quiz_attempt` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `quiz_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `start_date` DATETIME DEFAULT NULL,
  `end_date` DATETIME DEFAULT NULL,
  `correct` INT DEFAULT NULL,
  `incorrect` INT DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `quiz_attempt_quiz_id_fk_quiz_id` (`quiz_id`),
  KEY `quiz_attempt_user_id_fk_users_id` (`user_id`),
  CONSTRAINT `quiz_attempt_quiz_id_fk_quiz_id` FOREIGN KEY (`quiz_id`) REFERENCES `quiz` (`id`),
  CONSTRAINT `quiz_attempt_user_id_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `quiz_session` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `quiz_id` INT NOT NULL,
  `host_id` INT NOT NULL,
  `access_code` VARCHAR(20) NOT NULL,
  `start_time` DATETIME DEFAULT NULL,
  `end_time` DATETIME DEFAULT NULL,
  `is_active` INT DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `quiz_session_quiz_id_fk_quiz_id` (`quiz_id`),
  KEY `quiz_session_host_id_fk_users_id` (`host_id`),
  CONSTRAINT `quiz_session_quiz_id_fk_quiz_id` FOREIGN KEY (`quiz_id`) REFERENCES `quiz` (`id`),
  CONSTRAINT `quiz_session_host_id_fk_users_id` FOREIGN KEY (`host_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `quiz_user` (
  `quiz_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`quiz_id`, `user_id`),
  KEY `quiz_user_user_id_fk_users_id` (`user_id`),
  CONSTRAINT `quiz_user_quiz_id_fk_quiz_id` FOREIGN KEY (`quiz_id`) REFERENCES `quiz` (`id`),
  CONSTRAINT `quiz_user_user_id_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;