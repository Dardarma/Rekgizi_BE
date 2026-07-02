-- PostgreSQL initial schema for Rekgizi.
-- The order follows foreign-key dependencies from the SQLAlchemy models.

DO $$
BEGIN
    CREATE TYPE enum_role AS ENUM (
        'ahli_gizi',
        'pasien',
        'admin',
        'tenaga_kesehatan'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE enum_gender AS ENUM ('pria', 'wanita');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE enum_tipe_input AS ENUM (
        'text',
        'number',
        'boolean',
        'select',
        'textarea',
        'date'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE enum_status AS ENUM (
        'belum_ditinjau',
        'ditinjau',
        'disetujui'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE status_konseling AS ENUM (
        'pending',
        'approved',
        'rejected'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    role enum_role NOT NULL,
    nama VARCHAR(255) NOT NULL,
    jenis_kelamin enum_gender NOT NULL,
    alamat JSONB NOT NULL,
    tanggal_lahir DATE NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    pass_hash VARCHAR(255),
    reset_token TEXT,
    reset_token_expiry TIMESTAMP,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS intervensi (
    id SERIAL PRIMARY KEY,
    jenis_diet TEXT,
    tujuan TEXT,
    prinsip TEXT,
    edukasi TEXT,
    protein INTEGER,
    energi INTEGER,
    karbohidrat INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS parameter (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(255),
    kategori VARCHAR(50),
    tipe_input enum_tipe_input NOT NULL,
    important BOOLEAN DEFAULT FALSE,
    satuan VARCHAR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS diagnosa (
    id SERIAL PRIMARY KEY,
    kode VARCHAR,
    diagnosa VARCHAR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS opsi_parameter (
    id SERIAL PRIMARY KEY,
    parameter_id INTEGER REFERENCES parameter(id),
    jawaban TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jadwal_tersedia (
    id SERIAL PRIMARY KEY,
    konselor_id INTEGER NOT NULL REFERENCES users(id),
    day_of_week VARCHAR,
    start_time TIME,
    end_time TIME,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMP,
    CONSTRAINT chk_jadwal_tersedia_day_of_week CHECK (
        day_of_week IN (
            'Senin',
            'Selasa',
            'Rabu',
            'Kamis',
            'Jumat',
            'Sabtu',
            'Minggu'
        )
    )
);

CREATE TABLE IF NOT EXISTS jadwal_libur (
    id SERIAL PRIMARY KEY,
    jadwal_tersedia_id INTEGER NOT NULL REFERENCES jadwal_tersedia(id),
    tanggal DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    judul VARCHAR(255),
    konten TEXT,
    thumbnail_url VARCHAR(255),
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS rekam_pasien (
    id SERIAL PRIMARY KEY,
    pasien_id INTEGER REFERENCES users(id),
    tanggal_asesmen TIMESTAMP NOT NULL,
    status enum_status NOT NULL,
    intervensi_id INTEGER REFERENCES intervensi(id),
    tujuan_intervensi TEXT,
    jenis_diet TEXT,
    prinsip_intervensi TEXT,
    edukasi_intervensi TEXT,
    protein INTEGER,
    energi INTEGER,
    karbohidrat INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jadwal_konseling (
    id SERIAL PRIMARY KEY,
    pasien_id INTEGER REFERENCES users(id),
    konselor_id INTEGER REFERENCES users(id),
    jadwal_tersedia_id INTEGER NOT NULL REFERENCES jadwal_tersedia(id),
    tanggal_konseling DATE,
    status status_konseling NOT NULL DEFAULT 'pending',
    catatan TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rekam_pasien_parameter (
    id SERIAL PRIMARY KEY,
    rekam_pasien_id INTEGER REFERENCES rekam_pasien(id),
    parameter_id INTEGER REFERENCES parameter(id),
    opsi_parameter_id INTEGER REFERENCES opsi_parameter(id),
    jawaban TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS parameter_calculation (
    id SERIAL PRIMARY KEY,
    target_parameter_id INTEGER NOT NULL UNIQUE REFERENCES parameter(id),
    formula TEXT NOT NULL,
    rounding INTEGER DEFAULT 2,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS parameter_calculation_source (
    id SERIAL PRIMARY KEY,
    calculation_id INTEGER NOT NULL REFERENCES parameter_calculation(id) ON DELETE CASCADE,
    source_parameter_id INTEGER NOT NULL REFERENCES parameter(id),
    variable_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS diagnosa_pasien (
    id SERIAL PRIMARY KEY,
    id_rekam_pasien INTEGER NOT NULL REFERENCES rekam_pasien(id),
    id_diagnosa INTEGER NOT NULL REFERENCES diagnosa(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notification_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token VARCHAR NOT NULL,
    device_type VARCHAR(50) DEFAULT 'web',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_notification_tokens_token UNIQUE (token)
);

CREATE INDEX IF NOT EXISTS ix_articles_id ON articles(id);
CREATE INDEX IF NOT EXISTS ix_diagnosa_pasien_id ON diagnosa_pasien(id);
CREATE INDEX IF NOT EXISTS ix_intervensi_id ON intervensi(id);
CREATE INDEX IF NOT EXISTS ix_jadwal_konseling_id ON jadwal_konseling(id);
CREATE UNIQUE INDEX IF NOT EXISTS uq_jadwal_konseling_pasien_slot_active
    ON jadwal_konseling (
        pasien_id,
        konselor_id,
        jadwal_tersedia_id,
        tanggal_konseling
    )
    WHERE deleted_at IS NULL
      AND status IN ('pending', 'approved');
CREATE INDEX IF NOT EXISTS ix_jadwal_libur_id ON jadwal_libur(id);
CREATE INDEX IF NOT EXISTS ix_jadwal_tersedia_id ON jadwal_tersedia(id);
CREATE INDEX IF NOT EXISTS ix_jadwal_tersedia_konselor_id
    ON jadwal_tersedia(konselor_id);
CREATE INDEX IF NOT EXISTS ix_notification_tokens_id
    ON notification_tokens(id);
CREATE INDEX IF NOT EXISTS ix_notification_tokens_user_id
    ON notification_tokens(user_id);
CREATE INDEX IF NOT EXISTS ix_opsi_parameter_id ON opsi_parameter(id);
CREATE INDEX IF NOT EXISTS ix_parameter_id ON parameter(id);
CREATE INDEX IF NOT EXISTS ix_parameter_calculation_target_parameter_id
    ON parameter_calculation(target_parameter_id);
CREATE INDEX IF NOT EXISTS ix_parameter_calculation_source_calculation_id
    ON parameter_calculation_source(calculation_id);
CREATE INDEX IF NOT EXISTS ix_parameter_calculation_source_source_parameter_id
    ON parameter_calculation_source(source_parameter_id);
CREATE INDEX IF NOT EXISTS ix_rekam_pasien_id ON rekam_pasien(id);
