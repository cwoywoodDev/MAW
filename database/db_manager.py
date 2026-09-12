import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FOLDER = os.path.join(BASE_DIR, "BD")
DB_PATH = os.path.join(DB_FOLDER, "music_player.db")

def get_connection():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Tabla de Categorías
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        color_hex TEXT DEFAULT '#0F172A'
    );
    """)
    
    # 2. Tabla de Pistas de Audio
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pistas_audio (
        id TEXT PRIMARY KEY,
        titulo TEXT NOT NULL,
        categoria_id TEXT REFERENCES categorias(id) ON DELETE SET NULL,
        tipo_pista TEXT NOT NULL,
        ruta_archivo TEXT NOT NULL,
        es_bucle_perfecto INTEGER DEFAULT 1
    );
    """)
    
    # 3. Presets Guardados por el Usuario
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS presets_usuario (
        id TEXT PRIMARY KEY,
        nombre_mix TEXT NOT NULL,
        categoria_id TEXT REFERENCES categorias(id) ON DELETE CASCADE,
        pista_principal_id TEXT REFERENCES pistas_audio(id) ON DELETE CASCADE,
        temporizador_minutos INTEGER DEFAULT 45,
        fecha_creacion TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Detalle de Capas por Preset
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_preset_capas (
        preset_id TEXT REFERENCES presets_usuario(id) ON DELETE CASCADE,
        pista_ambiente_id TEXT REFERENCES pistas_audio(id) ON DELETE CASCADE,
        volumen_nivel REAL DEFAULT 0.5,
        PRIMARY KEY (preset_id, pista_ambiente_id)
    );
    """)
    
    # Insertar categorías iniciales solo si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM categorias;")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
        INSERT INTO categorias (id, nombre, descripcion, color_hex) 
        VALUES (?, ?, ?, ?);
        """, [
            ('sleep', 'Sueño', 'Música relajante, frecuencias suaves y sonidos de la naturaleza para descansar.', '#333A57'),
            ('focus', 'Concentración', 'Beats Lo-Fi, tonos binaurales y ritmos para enfoque profundo.', '#0F172A')
        ])
        
    conn.commit()
    conn.close()

def eliminar_pista_audio(id_pista):
    """Elimina una pista de la base de datos SQLite y su archivo físico del disco si existe."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT ruta_archivo FROM pistas_audio WHERE id = ?", (id_pista,))
    resultado = cursor.fetchone()
    
    if resultado:
        ruta_archivo = resultado[0]
        if os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
            except Exception:
                pass
        
        cursor.execute("DELETE FROM pistas_audio WHERE id = ?", (id_pista,))
        conn.commit()
        
    conn.close()

if __name__ == "__main__":
    init_db()