import os
from pathlib import Path

import mysql.connector


BASE_DIR = Path(__file__).resolve().parent


def load_env_file(path: Path = BASE_DIR / ".env") -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "setup_db")


TABLES = [
    """
    CREATE TABLE IF NOT EXISTS clientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        direccion VARCHAR(255) NULL,
        localidad VARCHAR(120) NULL,
        provincia VARCHAR(120) NULL,
        cp VARCHAR(30) NULL,
        telefono VARCHAR(60) NULL,
        celular VARCHAR(60) NULL,
        email VARCHAR(255) NULL,
        cuit VARCHAR(40) NULL,
        contacto VARCHAR(255) NULL,
        observaciones TEXT NULL,
        giro_empresa VARCHAR(255) NULL,
        cliente_garantia TINYINT(1) NOT NULL DEFAULT 0,
        cliente_con_contrato TINYINT(1) NOT NULL DEFAULT 0,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        KEY idx_clientes_nombre (nombre),
        KEY idx_clientes_telefono (telefono)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS equipos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        descripcion VARCHAR(255) NULL,
        serie VARCHAR(160) NULL,
        serie_norm VARCHAR(160) NULL,
        tipo VARCHAR(120) NULL,
        marca VARCHAR(120) NULL,
        modelo VARCHAR(120) NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uq_equipos_serie_norm (serie_norm),
        KEY idx_equipos_descripcion (descripcion)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS equipo_cliente (
        id INT AUTO_INCREMENT PRIMARY KEY,
        equipo_id INT NOT NULL,
        cliente_id INT NOT NULL,
        rol VARCHAR(80) NOT NULL DEFAULT 'propietario',
        fecha_asignacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        activo TINYINT(1) NOT NULL DEFAULT 1,
        UNIQUE KEY uq_equipo_cliente (equipo_id, cliente_id),
        KEY idx_equipo_cliente_activo (equipo_id, activo),
        CONSTRAINT fk_equipo_cliente_equipo
            FOREIGN KEY (equipo_id) REFERENCES equipos(id)
            ON DELETE CASCADE,
        CONSTRAINT fk_equipo_cliente_cliente
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS fallas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        descripcion VARCHAR(255) NOT NULL,
        UNIQUE KEY uq_fallas_descripcion (descripcion)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS reparaciones (
        id INT AUTO_INCREMENT PRIMARY KEY,
        descripcion VARCHAR(255) NOT NULL,
        UNIQUE KEY uq_reparaciones_descripcion (descripcion)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS repuestos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        descripcion TEXT NULL,
        costo DECIMAL(12,2) NOT NULL DEFAULT 0.00,
        UNIQUE KEY uq_repuestos_nombre (nombre),
        KEY idx_repuestos_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS accesorios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        UNIQUE KEY uq_accesorios_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS ordenes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fecha DATE NOT NULL,
        hora_ingreso TIME NULL,
        cliente_id INT NOT NULL,
        equipo_id INT NOT NULL,
        falla TEXT NULL,
        observaciones TEXT NULL,
        accesorios TEXT NULL,
        reparacion TEXT NULL,
        repuestos TEXT NULL,
        importe DECIMAL(12,2) NOT NULL DEFAULT 0.00,
        estado VARCHAR(80) NOT NULL DEFAULT 'EN REPARACION',
        fecha_salida DATE NULL,
        hora_salida TIME NULL,
        fecha_regreso DATE NULL,
        hora_regreso TIME NULL,
        fecha_retiro DATE NULL,
        hora_retiro TIME NULL,
        fecha_terminada DATE NULL,
        hora_terminada TIME NULL,
        presupuesto_aprobado TINYINT(1) NOT NULL DEFAULT 0,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        KEY idx_ordenes_estado (estado),
        KEY idx_ordenes_fecha (fecha),
        KEY idx_ordenes_cliente (cliente_id),
        KEY idx_ordenes_equipo (equipo_id),
        CONSTRAINT fk_ordenes_cliente
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        CONSTRAINT fk_ordenes_equipo
            FOREIGN KEY (equipo_id) REFERENCES equipos(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS orden_historial (
        id INT AUTO_INCREMENT PRIMARY KEY,
        orden_id INT NOT NULL,
        usuario VARCHAR(120) NOT NULL DEFAULT 'sistema',
        accion VARCHAR(80) NOT NULL,
        nota TEXT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        KEY idx_historial_orden (orden_id),
        CONSTRAINT fk_historial_orden
            FOREIGN KEY (orden_id) REFERENCES ordenes(id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
]


SEED_DATA = [
    ("fallas", "descripcion", ["No enciende", "No imprime", "Falla intermitente"]),
    ("reparaciones", "descripcion", ["Revision", "Limpieza", "Cambio de repuesto"]),
]


def main() -> None:
    try:
        server_conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        server_conn.autocommit = True
        cur = server_conn.cursor()
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cur.close()
        server_conn.close()
    except mysql.connector.Error as exc:
        print(
            "No pude crear/verificar la base a nivel servidor. "
            "Si la base ya existe y el usuario tiene permisos sobre ella, sigo igual. "
            f"Detalle: {exc}"
        )

    conn = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
    )
    cur = conn.cursor()
    for statement in TABLES:
        cur.execute(statement)

    for table, column, values in SEED_DATA:
        for value in values:
            cur.execute(
                f"INSERT IGNORE INTO `{table}` (`{column}`) VALUES (%s)",
                (value,),
            )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Base de datos lista: {DB_NAME}")


if __name__ == "__main__":
    main()
