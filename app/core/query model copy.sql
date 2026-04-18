-- =========================
-- ENUMS
-- =========================
CREATE TYPE enum_status AS ENUM ('belum_ditinjau', 'ditinjau', 'disetujui');
CREATE TYPE enum_status_jadwal AS ENUM ('pending', 'approved', 'rejected');
CREATE TYPE enum_tipe_input AS ENUM ('text','number','boolean','select','textarea', 'date');
CREATE TYPE enum_role AS ENUM ('ahli_gizi', 'pasien', 'admin', 'tenaga_kesehatan');
CREATE TYPE enum_gender AS ENUM ('pria','wanita');

-- =========================
-- TABEL USERS
-- =========================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    role enum_role NOT NULL DEFAULT 'pasien',
    nama VARCHAR(255) NOT NULL,
    jenis_kelamin enum_gender NOT NULL
    alamat JSONB NOT NULL,
    tanggal_lahir DATE NOT NULL,

    email VARCHAR(255) UNIQUE NOT NULL,
    pass_hash VARCHAR(255), 
    reset_token TEXT,
    reset_token_expiry TIMESTAMP,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- =========================
-- TABEL INTERVENSI
-- =========================
CREATE TABLE intervensi (
    id SERIAL PRIMARY KEY,
    tujuan TEXT NOT NULL,
    prinsip TEXT NOT NULL,
    rencana_diet TEXT NOT NULL,
    edukasi TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- =========================
-- TABEL PARAMETER
-- =========================
CREATE TABLE parameter (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(255) NOT NULL,
    kategori VARCHAR(50) NOT NULL,
    tipe_input enum_tipe_input NOT NULL DEFAULT 'text',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- =========================
-- TABEL OPSI PARAMETER
-- =========================
CREATE TABLE opsi_parameter (
    id SERIAL PRIMARY KEY,
    parameter_id INTEGER NOT NULL,
    jawaban TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    FOREIGN KEY (parameter_id) REFERENCES parameter(id)
);

-- =========================
-- TABEL JADWAL TERSEDIA
-- =========================
CREATE TABLE jadwal_tersedia (
    id SERIAL PRIMARY KEY,
    konselor_id INTEGER NOT NULL,
    day_of_week VARCHAR(10),

    start_time TIME NOT NULL,
    end_time TIME NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    FOREIGN KEY (konselor_id) REFERENCES users(id)
);

-- =========================
-- TABEL JADWAL LIBUR
-- =========================
CREATE TABLE jadwal_libur (
    id SERIAL PRIMARY KEY,
    jadwal_tersedia_id INTEGER NOT NULL,
    tanggal DATE NOT NULL,
    start_time TIME,
    end_time TIME,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    FOREIGN KEY (jadwal_tersedia_id) REFERENCES jadwal_tersedia(id)
);

-- =========================
-- TABEL JADWAL KONSELING
-- =========================
CREATE TABLE jadwal_konseling (
    id SERIAL PRIMARY KEY,
    pasien_id INTEGER NOT NULL,
    konselor_id INTEGER NOT NULL,

    tanggal_konseling DATE NOT NULL,
    status enum_status_jadwal NOT NULL DEFAULT 'pending',

    catatan TEXT NOT NULL,
    jadwal_tersedia_id INTEGER NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    FOREIGN KEY (pasien_id) REFERENCES users(id),
    FOREIGN KEY (konselor_id) REFERENCES users(id),
    FOREIGN KEY (jadwal_tersedia_id) REFERENCES jadwal_tersedia(id)
);

-- =========================
-- TABEL ARTIKEL
-- =========================
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    judul VARCHAR(255) NOT NULL,
    konten TEXT,
    is_published BOOLEAN NOT NULL DEFAULT false,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- =========================
-- TABEL REKAM PASIEN
-- =========================
CREATE TABLE rekam_pasien (
    id SERIAL PRIMARY KEY,
    pasien_id INTEGER NOT NULL,
    tanggal_asesmen TIMESTAMP NOT NULL,

    status enum_status NOT NULL DEFAULT 'belum_ditinjau',
    intervensi_id INTEGER,

    -- snapshot intervensi
    tujuan_intervensi TEXT,
    prinsip_intervensi TEXT,
    rencana_diet_intervensi TEXT,
    edukasi_intervensi TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    FOREIGN KEY (pasien_id) REFERENCES users(id),
    FOREIGN KEY (intervensi_id) REFERENCES intervensi(id)
);

-- =========================
-- TABEL DETAIL PARAMETER REKAM PASIEN
-- =========================
CREATE TABLE rekam_pasien_parameter (
    id SERIAL PRIMARY KEY,
    rekam_pasien_id INTEGER NOT NULL,
    parameter_id INTEGER NOT NULL,
    opsi_parameter_id INTEGER,
    jawaban TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    UNIQUE (rekam_pasien_id, parameter_id),

    CHECK (
    jawaban IS NOT NULL
    OR opsi_parameter_id IS NOT NULL
    ),

    FOREIGN KEY (rekam_pasien_id) REFERENCES rekam_pasien(id),
    FOREIGN KEY (parameter_id) REFERENCES parameter(id),
    FOREIGN KEY (opsi_parameter_id) REFERENCES opsi_parameter(id),
);

-- =========================
-- TABEL DIAGNOSA
-- =========================
CREATE TABLE diagnosa (
    id SERIAL PRIMARY KEY,
    kode VARCHAR (255) NOT NULL,
    diagnosa VARCHAR (255) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ

);

-- =========================
-- TABEL DIAGNOSA_PASIEN
-- =========================
CREATE TABLE diagnosa_pasien (
    id SERIAL PRIMARY KEY,
    id_rekam_pasien INTEGER NOT NULL,
    id_diagnosa Integer NOT NULL,

    FOREIGN KEY (id_rekam_pasien) REFERENCES rekam_pasien(id),
    FOREIGN KEY (id_diagnosa) REFERENCES diagnosa(id),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);