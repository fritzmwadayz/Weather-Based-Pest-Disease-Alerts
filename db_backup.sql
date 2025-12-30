PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version VALUES('cae6445a1c4f');
CREATE TABLE pest_report (
	id INTEGER NOT NULL, 
	crop_type VARCHAR(50) NOT NULL, 
	pest_name VARCHAR(50) NOT NULL, 
	severity VARCHAR(50) NOT NULL, 
	date_reported DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE prediction_log (
	id INTEGER NOT NULL, 
	crop_type VARCHAR(50) NOT NULL, 
	prediction VARCHAR(200) NOT NULL, 
	date_predicted DATETIME, 
	PRIMARY KEY (id)
);
CREATE TABLE user (
	id INTEGER NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(128) NOT NULL, 
	role VARCHAR(10) DEFAULT 'farmer' NOT NULL, settings JSON, 
	PRIMARY KEY (id), 
	UNIQUE (email), 
	UNIQUE (username)
);
INSERT INTO user VALUES(1,'test','test@test.com','scrypt:32768:8:1$JB7kHnhap1qHR66R$5e45cbcac30b7dc23159f87e7a4537932163613cdf6aae39f2004b0b16164f35ec15bfe1611a6b4648eb635151ec82840323f0ce998405c770daca595b507958','farmer',NULL);
INSERT INTO user VALUES(2,'admin','admin@example.com','scrypt:32768:8:1$CgunkVNxBJofwGEs$89f09ebbb172accda8eb5caf8d0445ad4edbca9fab119de874638b9e2b50347a8d27c9c0883305f4bfa3d8ed39bf3ea6e093228316cdd7d9f4c96bd6238d287b','admin',NULL);
INSERT INTO user VALUES(3,'testuser','test@example.com','scrypt:32768:8:1$3RJjUZuL9e7cRdNC$aa80c90a91212b651cd055440e42a6e2d3b4313d1b282c92e535a513a8843d69c3c9f7ebcf926d23e10e83414669799fd38b1e4555b5582faaa3df8d1a63cef5','farmer',NULL);
INSERT INTO user VALUES(4,'test2','test2@test.com','scrypt:32768:8:1$Ngduq4yxrhK1Eohm$1e65ae326289a65ce1c711e814e622242270dd9cb9f4316c8254ea1dc6fb1b9abc6ca25ca06b1e707ecf6dfe5e7a9d9fb78544b7adb1d4b349e032a4be06a061','farmer',NULL);
CREATE TABLE crop (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, recommended_model VARCHAR(100), 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO crop VALUES(1,'Maize',NULL);
INSERT INTO crop VALUES(2,'Wheat',NULL);
INSERT INTO crop VALUES(3,'maize',NULL);
INSERT INTO crop VALUES(4,'wheat',NULL);
INSERT INTO crop VALUES(5,'rice',NULL);
CREATE TABLE farm_crops (
	farm_id INTEGER NOT NULL, 
	crop_id INTEGER NOT NULL, 
	PRIMARY KEY (farm_id, crop_id), 
	FOREIGN KEY(crop_id) REFERENCES crop (id), 
	FOREIGN KEY(farm_id) REFERENCES farm (id)
);
INSERT INTO farm_crops VALUES(1,4);
CREATE TABLE IF NOT EXISTS "farm" (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	location VARCHAR(255) NOT NULL, temperature FLOAT, created_at DATETIME, updated_at DATETIME, 
	PRIMARY KEY (id), 
	CONSTRAINT fk_farm_user FOREIGN KEY(user_id) REFERENCES user (id)
);
INSERT INTO farm VALUES(1,1,'Taita Hills',NULL,'2025-03-26 07:27:04.713797','2025-03-27 06:38:10.506399');
CREATE TABLE blog_post (
	id INTEGER NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	content TEXT NOT NULL, 
	author VARCHAR(100) NOT NULL, 
	created_at DATETIME, 
	tags JSON, 
	PRIMARY KEY (id)
);
CREATE TABLE alert_blog_association (
	alert_id INTEGER NOT NULL, 
	blog_post_id INTEGER NOT NULL, 
	PRIMARY KEY (alert_id, blog_post_id), 
	FOREIGN KEY(alert_id) REFERENCES alert (id), 
	FOREIGN KEY(blog_post_id) REFERENCES blog_post (id)
);
CREATE TABLE IF NOT EXISTS "alert" (
	id INTEGER NOT NULL, 
	farm_id INTEGER NOT NULL, 
	pest_name VARCHAR(100) NOT NULL, 
	risk_level VARCHAR(20) NOT NULL, 
	created_at DATETIME, 
	is_active BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(farm_id) REFERENCES farm (id)
);
COMMIT;
