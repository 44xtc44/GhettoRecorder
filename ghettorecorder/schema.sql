DROP TABLE IF EXISTS GhettoRecorder;
DROP TABLE IF EXISTS GRAction;

CREATE TABLE "GhettoRecorder" (
	"id"	INTEGER NOT NULL,
	"created"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "http_srv" INTEGER,
 	PRIMARY KEY("id" AUTOINCREMENT)
)
;
CREATE TABLE "GRAction" (
	"id"	INTEGER NOT NULL,
	"created"	TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"stop" INTEGER,
    "radio_name" TEXT NOT NULL,
    "runs_meta" INTEGER,
    "runs_record" INTEGER,
    "record_stop" INTEGER,
    "recorder_file_write" INTEGER,
    "runs_listen" INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
)
;
