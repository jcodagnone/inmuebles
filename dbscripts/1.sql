BEGIN;

-- para saber hasta que db script se corrio
CREATE TABLE alquiler_version (
    version serial PRIMARY KEY,
    date timestamp NOT NULL DEFAULT  CURRENT_TIMESTAMP
);


-- guarda los lugares que bajamos desde clarin
CREATE TABLE places(
     ID bigserial PRIMARY KEY,
     DATE timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
     provider   varchar(16) NOT NULL,
     providerID varchar(16) NOT NULL
);
SELECT AddGeometryColumn('', 'places','the_geom', 4326,'POINT',2);
CREATE INDEX places_thegeom_idx ON places USING gist(the_geom);

-- guarda las propiedades de los lugares que bajamos de clarin
CREATE TABLE places_description(
     id    int8 references places(id) ON DELETE CASCADE,
     name text NOT NULL,
     value text NOT NULL
);

-- comentarios del foro
CREATE TABLE places_forum (
     ID bigserial PRIMARY KEY,
     idPlace    int8 references places(id) ON DELETE CASCADE,
     owner varchar(12) NOT NULL,
     description  text NOT NULL,
     DATE timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- logs
CREATE TABLE action_log (
    owner varchar(16),
    description text,
    date timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- fin del script...subimos la version
INSERT INTO alquiler_version VALUES (1);
END;
