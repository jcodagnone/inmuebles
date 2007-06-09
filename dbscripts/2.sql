BEGIN;
CREATE TABLE places_states(
    state varchar(16) PRIMARY KEY
);
INSERT INTO places_states VALUES('IMPORTADO');
INSERT INTO places_states VALUES('POSIBLE');
INSERT INTO places_states VALUES('NO DISPONIBLE');

ALTER TABLE places ADD COLUMN state varchar(16) references places_states(state)
DEFAULT 'IMPORTADO';


END;
