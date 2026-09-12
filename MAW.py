import streamlit as st
import os
import time
import pandas as pd
import streamlit.components.v1 as components
from database.db_manager import get_connection, init_db, eliminar_pista_audio
from styles.dark_theme import aplicar_tema_sueno, aplicar_tema_focus

# Configuración inicial de la página
st.set_page_config(
    page_title="MAW Player",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Base de Datos
init_db()

# Navegación superior horizontal
st.markdown("### 🎵 Selector de Categorías")
col_nav1, col_nav2 = st.columns([3, 1])
with col_nav1:
    modo = st.radio(
        "Seleccionar:", 
        ["🌙 Sueño", "🎯 Concentración Focus", "⚙️ Administración"], 
        horizontal=True,
        label_visibility="collapsed"
    )
with col_nav2:
    modo_continuo = st.toggle("🔁 Reproducción Continua", value=False)

st.markdown("---")

if "Sueño" in modo:
    aplicar_tema_sueno()
    
    st.title("🌙 Modo Sueño")
    st.caption("Música relajante, frecuencias suaves y mezcla de paisajes sonoros nocturnos.")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, titulo, ruta_archivo 
        FROM pistas_audio 
        WHERE categoria_id = 'sleep' AND tipo_pista = 'principal'
    """)
    pistas_principales_db = cursor.fetchall()

    cursor.execute("""
        SELECT id, titulo, ruta_archivo 
        FROM pistas_audio 
        WHERE categoria_id = 'sleep' AND tipo_pista = 'ambiente'
    """)
    pistas_ambiente_db = cursor.fetchall()
    conn.close()

    opciones_principales = {
        titulo: ruta.replace("\\", "/") for id_p, titulo, ruta in pistas_principales_db
    } if pistas_principales_db else {
        "Tranquility Base (Respaldo)": "assets/music/Tranquility.mp3"
    }

    # CONTENEDOR REPRODUCTOR PRINCIPAL
    with st.container(border=True):
        st.subheader("Pista Base Principal")
        if opciones_principales:
            pista_seleccionada = st.selectbox(
                "Selecciona una pista registrada para escuchar:", 
                list(opciones_principales.keys()),
                key="select_sleep_main"
            )
            ruta_audio_actual = opciones_principales[pista_seleccionada]

            col1, col2 = st.columns([2, 3])
            with col1:
                if os.path.exists(ruta_audio_actual):
                    es_loop = not modo_continuo
                    st.audio(ruta_audio_actual, format="audio/mp3", loop=es_loop)
                else:
                    st.warning(f"⚠️ El archivo no se encuentra en la ruta: '{ruta_audio_actual}'.")
            with col2:
                vol_main = st.slider("Volumen Principal", 0, 100, 70, key="vol_main_sleep")
        else:
            st.info("No hay pistas principales guardadas.")
            vol_main = 70

    # CONTENEDOR MEZCLADOR AMBIENTAL MULTI-CAPA
    volumenes_ambiente = []
    with st.container(border=True):
        st.subheader("🎛️ Mezclador de Capas Ambientales")
        
        if pistas_ambiente_db:
            st.markdown("### Capas de Fondo Activas")
            for idx_a, (id_a, tit_a, rut_a) in enumerate(pistas_ambiente_db):
                rut_a_norm = rut_a.replace("\\", "/")
                c_a1, c_a2 = st.columns([2, 3])
                with c_a1:
                    st.markdown(f"**🔊 {tit_a}**")
                    if os.path.exists(rut_a_norm):
                        st.audio(rut_a_norm, format="audio/mp3", loop=True)
                    else:
                        st.error(f"⚠️ Archivo '{rut_a_norm}' no encontrado.")
                with c_a2:
                    v_amb_val = st.slider(f"Volumen: {tit_a}", 0, 100, 40, key=f"vol_amb_db_{id_a}_{idx_a}")
                    volumenes_ambiente.append(v_amb_val / 100.0)
            st.markdown("---")

        c1, c2, c3 = st.columns(3)
        ruta_tormenta = "assets/ambient/tormenta1.mp3"
        ruta_marron = "assets/ambient/ruido_marron.mp3"
        ruta_viento = "assets/ambient/viento.mp3"

        with c1:
            st.markdown("**⚡ Tormenta 1**")
            if os.path.exists(ruta_tormenta):
                st.audio(ruta_tormenta, format="audio/mp3", loop=True)
            else:
                st.error("⚠️ Archivo no encontrado.")
            vol_tormenta = st.slider("Tormenta", 0, 100, 40, key="vol_tormenta_sleep")

        with c2:
            st.markdown("**☕ Ruido Marrón**")
            if os.path.exists(ruta_marron):
                st.audio(ruta_marron, format="audio/mp3", loop=True)
            else:
                st.error("⚠️ Archivo no encontrado.")
            vol_marron = st.slider("Ruido Marrón", 0, 100, 20, key="vol_marron_sleep")

        with c3:
            st.markdown("**🍃 Viento Nocturno**")
            if os.path.exists(ruta_viento):
                st.audio(ruta_viento, format="audio/mp3", loop=True)
            else:
                st.error("⚠️ Archivo no encontrado.")
            vol_viento = st.slider("Viento", 0, 100, 0, key="vol_viento_sleep")

    v_main_f = vol_main / 100.0
    v_tormenta_f = vol_tormenta / 100.0
    v_marron_f = vol_marron / 100.0
    v_viento_f = vol_viento / 100.0

    js_amb_array = str(volumenes_ambiente)

    js_code = f"""
    <script>
        function aplicarNivelVolumenes() {{
            const doc = window.parent.document;
            const audioElements = doc.querySelectorAll('audio');
            
            audioElements.forEach(aud => {{
                aud.setAttribute('controlsList', 'nodownload noplaybackrate nooverflow');
                aud.disableRemotePlayback = true;
            }});

            if (audioElements.length > 0) {{
                let idx = 0;
                if (audioElements[idx]) {{ audioElements[idx].volume = {v_main_f}; idx++; }}
                
                const volsBD = {js_amb_array};
                volsBD.forEach(v => {{
                    if (audioElements[idx]) {{ audioElements[idx].volume = v; idx++; }}
                }});

                if (audioElements[idx]) {{ audioElements[idx].volume = {v_tormenta_f}; idx++; }}
                if (audioElements[idx]) {{ audioElements[idx].volume = {v_marron_f}; idx++; }}
                if (audioElements[idx]) {{ audioElements[idx].volume = {v_viento_f}; idx++; }}
            }}
        }}
        aplicarNivelVolumenes();
        setTimeout(aplicarNivelVolumenes, 500);
    </script>
    """
    components.html(js_code, height=0, width=0)

elif "Concentración" in modo:
    aplicar_tema_focus()
    
    st.title("🎯 Modo Concentración (Focus)")
    st.caption("Beats Lo-Fi, ondas binaurales y frecuencias para optimizar el trabajo profundo.")

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, titulo, ruta_archivo 
        FROM pistas_audio 
        WHERE categoria_id = 'focus' AND tipo_pista = 'principal'
    """)
    pistas_focus_db = cursor.fetchall()
    conn.close()

    opciones_focus = {
        titulo: ruta.replace("\\", "/") for id_p, titulo, ruta in pistas_focus_db
    } if pistas_focus_db else {
        "Lo-Fi Study Beats (Respaldo)": "assets/music/lofi01.mp3"
    }

    # REPRODUCTOR FOCUS PRINCIPAL
    with st.container(border=True):
        st.subheader("🎧 Pistas de Enfoque Guardadas")
        if opciones_focus:
            focus_seleccionado = st.selectbox(
                "Selecciona la sesión de concentración (.mp3):", 
                list(opciones_focus.keys()),
                key="select_focus_main"
            )
            ruta_focus_actual = opciones_focus[focus_seleccionado]

            f_col1, f_col2 = st.columns([2, 3])
            with f_col1:
                if os.path.exists(ruta_focus_actual):
                    st.audio(ruta_focus_actual, format="audio/mp3", loop=not modo_continuo)
                else:
                    st.warning(f"⚠️ El archivo no existe en la ruta: '{ruta_focus_actual}'.")
            with f_col2:
                vol_focus_main = st.slider("Volumen Focus", 0, 100, 80, key="vol_focus_main")
        else:
            st.info("No hay pistas de focus guardadas.")
            vol_focus_main = 80

    # MEZCLADOR DE CAPAS AMBIENTALES EN FOCUS (Con los archivos reales de tu carpeta ambient)
    volumenes_focus_amb = []
    with st.container(border=True):
        st.subheader("🎛️ Capas Ambientales de Fondo para Focus")
        
        fc1, fc2, fc3 = st.columns(3)
        ruta_lluvia_cafeteria = "assets/ambient/lluvia_cafeteria.mp3"
        ruta_alfa = "assets/ambient/alfa_10hz.mp3"
        ruta_lluvia01 = "assets/ambient/lluvia001.mp3"

        with fc1:
            st.markdown("**☕ Lluvia Cafetería**")
            if os.path.exists(ruta_lluvia_cafeteria):
                st.audio(ruta_lluvia_cafeteria, format="audio/mp3", loop=True)
            else:
                st.error("⚠️ Archivo no encontrado.")
            vol_cafeteria = st.slider("Cafetería", 0, 100, 30, key="vol_cafeteria_focus")

        with fc2:
            st.markdown("**🧠 Ondas Alpha (10 Hz)**")
            if os.path.exists(ruta_alfa):
                st.audio(ruta_alfa, format="audio/mp3", loop=True)
            else:
                st.error("⚠️ Archivo no encontrado.")
            vol_alfa = st.slider("Ondas Alpha", 0, 100, 25, key="vol_alfa_focus")

        with fc3:
            st.markdown("**🌧️ Lluvia Suave**")
            if os.path.exists(ruta_lluvia01):
                st.audio(ruta_lluvia01, format="audio/mp3", loop=True)
            else:
                st.error("⚠️ Archivo no encontrado.")
            vol_lluvia01 = st.slider("Lluvia Suave", 0, 100, 20, key="vol_lluvia01_focus")

    vf_main = vol_focus_main / 100.0
    vf_cafeteria = vol_cafeteria / 100.0
    vf_alfa = vol_alfa / 100.0
    vf_lluvia01 = vol_lluvia01 / 100.0

    js_code_focus = f"""
    <script>
        function aplicarAjustesFocus() {{
            const doc = window.parent.document;
            const audioElements = doc.querySelectorAll('audio');
            
            audioElements.forEach(aud => {{
                aud.setAttribute('controlsList', 'nodownload noplaybackrate nooverflow');
                aud.disableRemotePlayback = true;
            }});

            if (audioElements.length > 0) {{
                let idx = 0;
                if (audioElements[idx]) {{ audioElements[idx].volume = {vf_main}; idx++; }}
                if (audioElements[idx]) {{ audioElements[idx].volume = {vf_cafeteria}; idx++; }}
                if (audioElements[idx]) {{ audioElements[idx].volume = {vf_alfa}; idx++; }}
                if (audioElements[idx]) {{ audioElements[idx].volume = {vf_lluvia01}; idx++; }}
            }}
        }}
        aplicarAjustesFocus();
        setTimeout(aplicarAjustesFocus, 500);
    </script>
    """
    components.html(js_code_focus, height=0, width=0)

elif "Administración" in modo:
    aplicar_tema_sueno()
    
    st.title("⚙️ Módulo de Administración")
    st.caption("Gestión e ingreso de nuevas pistas de audio.")

    if "titulo_auto" not in st.session_state:
        st.session_state["titulo_auto"] = ""

    with st.container(border=True):
        st.subheader("📤 Registrar Nueva Pista en la Base de Datos")

        archivo_audio = st.file_uploader(
            "Selecciona un archivo de audio (.mp3, .wav):", 
            type=["mp3", "wav"],
            key="uploader_audio"
        )

        if archivo_audio is not None:
            nombre_sin_extension = os.path.splitext(archivo_audio.name)[0]
            if st.session_state.get("ultimo_archivo") != archivo_audio.name:
                st.session_state["titulo_auto"] = nombre_sin_extension
                st.session_state["ultimo_archivo"] = archivo_audio.name

        with st.form("form_admin_pistas", clear_on_submit=True):
            titulo_pista = st.text_input(
                "Título de la Pista:", 
                value=st.session_state["titulo_auto"]
            )
            tipo_pista = st.selectbox("Tipo de Pista:", ["principal", "ambiente"])
            categoria_pista = st.selectbox("Categoría:", ["sleep", "focus"])
            
            btn_guardar = st.form_submit_button("REGISTRAR Y GUARDAR PISTA")
            
            if btn_guardar:
                if titulo_pista.strip() and archivo_audio is not None:
                    subcarpeta = "music" if tipo_pista == "principal" else "ambient"
                    directorio_destino = os.path.join("assets", subcarpeta)
                    os.makedirs(directorio_destino, exist_ok=True)
                    
                    nombre_archivo_seguro = archivo_audio.name
                    ruta_guardado = f"assets/{subcarpeta}/{nombre_archivo_seguro}"
                    
                    ruta_fisica_local = os.path.join(directorio_destino, nombre_archivo_seguro)
                    with open(ruta_fisica_local, "wb") as f:
                        f.write(archivo_audio.getbuffer())
                    
                    conn = get_connection()
                    cursor = conn.cursor()
                    id_pista = f"pista_{int(time.time()*1000)}"
                    cursor.execute("""
                        INSERT INTO pistas_audio (id, titulo, categoria_id, tipo_pista, ruta_archivo, es_bucle_perfecto)
                        VALUES (?, ?, ?, ?, ?, 1)
                    """, (id_pista, titulo_pista.strip(), categoria_pista, tipo_pista, ruta_guardado))
                    conn.commit()
                    conn.close()
                    
                    st.session_state["titulo_auto"] = ""
                    st.session_state["ultimo_archivo"] = None
                    
                    st.success(f"¡Pista '{titulo_pista}' registrada correctamente!")
                    st.rerun()
                else:
                    st.warning("Debe ingresar un título válido y adjuntar un archivo de audio.")

    with st.container(border=True):
        st.subheader("📋 Catálogo Registrado (`pistas_audio`)")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, titulo, categoria_id, tipo_pista, ruta_archivo FROM pistas_audio")
        registros = cursor.fetchall()
        conn.close()

        if registros:
            for reg in registros:
                p_id, p_titulo, p_cat, p_tipo, p_ruta = reg
                with st.container(border=True):
                    col_detalles, col_accion = st.columns([4, 1])
                    with col_detalles:
                        st.markdown(f"**{p_titulo}** `[{p_id}]`")
                        st.caption(f"📁 Categoría: **{p_cat.upper()}** | Tipo: **{p_tipo}** | Ruta: `{p_ruta}`")
                    with col_accion:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🗑️ Eliminar", key=f"btn_del_pista_{p_id}"):
                            eliminar_pista_audio(p_id)
                            st.toast(f"Pista '{p_titulo}' eliminada.")
                            st.rerun()
        else:
            st.info("No hay pistas guardadas actualmente en la base de datos.")
