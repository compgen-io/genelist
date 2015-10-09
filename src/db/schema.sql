DROP TABLE IF EXISTS gene_list_evidence;
DROP TABLE IF EXISTS gene_list;
DROP TABLE IF EXISTS evidence;
DROP TABLE IF EXISTS lists;
DROP TABLE IF EXISTS gene_aliases;
DROP TABLE IF EXISTS genes;
DROP TABLE IF EXISTS orgs;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
	id SERIAL PRIMARY KEY,
	username VARCHAR(255) UNIQUE NOT NULL,
	password VARCHAR(1024) NOT NULL,
	is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE orgs (
	id SERIAL PRIMARY KEY,
	common_name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE genes (
	id SERIAL PRIMARY KEY,
	org_id INTEGER NOT NULL REFERENCES orgs(id),
	genename VARCHAR(255) NOT NULL,
	original_name VARCHAR(255) NOT NULL,
	ncbi_geneid VARCHAR(255) UNIQUE,
	ncbi_refseqid VARCHAR(255) UNIQUE,
	ensembl_geneid VARCHAR(255) UNIQUE,
    UNIQUE(org_id, genename)
);

CREATE TABLE gene_aliases (
	gene_id INTEGER NOT NULL REFERENCES genes(id),
	alias VARCHAR(255)
);

CREATE TABLE lists (
	id SERIAL PRIMARY KEY,
	name VARCHAR(1024) NOT NULL,
	org_id INTEGER NOT NULL REFERENCES orgs(id),
	parent_id INTEGER REFERENCES lists(id),
	is_public BOOLEAN DEFAULT TRUE
);

CREATE TABLE evidence (
	id SERIAL PRIMARY KEY,
	title TEXT,
	citation TEXT,
	abstract TEXT,
	url TEXT UNIQUE,
	pubmed_id VARCHAR(255) UNIQUE
);

CREATE TABLE gene_list (
	list_id INTEGER NOT NULL REFERENCES lists(id),
	gene_id INTEGER NOT NULL REFERENCES genes(id),
	added_by INTEGER REFERENCES users(id),
	added_timestamp TIMESTAMP NOT NULL DEFAULT now(),
	notes TEXT,
    PRIMARY KEY (list_id, gene_id)
 );

CREATE TABLE gene_list_evidence (
	list_id INTEGER NOT NULL REFERENCES lists(id),
	gene_id INTEGER NOT NULL REFERENCES genes(id),
	evidence_id INTEGER NOT NULL REFERENCES evidence(id),
	PRIMARY KEY (list_id, gene_id, evidence_id)
);

INSERT INTO users (username, password, is_admin) VALUES ('sa', 'pbkdf2$d66545c53de8a162443ddc6fab4348bf$82cc46bfb92eea0062ed4fc378b7f99f42cf71711aeb388e225e70fbf0030a92', TRUE);
INSERT INTO orgs (common_name) VALUES ('Human');
