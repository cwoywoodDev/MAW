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

# CSS para asegurar que el botón del menú lateral sea visible en celulares
st.markdown("""
<style>
    /* Forzar visibilidad del botón de despliegue lateral en dispositivos móviles */
    header {
        visibility: visible !important;
        background: transparent !important;
    }
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: block !important;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar Base de Datos
init_db()

# Navegación lateral
st.sidebar.title("🎵 Categorías")
modo = st.sidebar.radio("Seleccionar:", ["🌙 Sueño", "🎯 Concentración Focus", "⚙️ Administración"])

st.sidebar.markdown("---")
modo_continuo = st.sidebar.toggle("🔁 Reproducción Continua (Playlist)", value=False)

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

    opciones_principales = {titulo: ruta for id_p, titulo, ruta in pistas_principales_db} if pistas_principales_db else {
        "Olas Nocturnas & Frecuencia Delta": os.path.join("assets", "music", "olas_delta.mp3")
    }

    # CONTENEDOR REPRODUCTOR PRINCIPAL
    with st.container(border=True):
        st.subheader("Pista Base Principal")
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
                st.warning(f"⚠️ El archivo de audio no se encuentra en la ruta: '{ruta_audio_actual}'. Regístralo en Administración.")
        with col2:
            vol_main = st.slider("Volumen Principal", 0, 100, 70, key="vol_main_sleep")

    # CONTENEDOR MEZCLADOR AMBIENTAL MULTI-CAPA
    volumenes_ambiente = []
    with st.container(border=True):
        st.subheader("🎛️ Mezclador de Capas Ambientales (Múltiples Sonidos)")
        
        if pistas_ambiente_db:
            st.markdown("### Capas de Fondo Activas")
            for idx_a, (id_a, tit_a, rut_a) in enumerate(pistas_ambiente_db):
                c_a1, c_a2 = st.columns([2, 3])
                with c_a1:
                    st.markdown(f"**🔊 {tit_a}**")
                    if os.path.exists(rut_a):
                        st.audio(rut_a, format="audio/mp3", loop=True)
                    else:
                        st.error(f"⚠️ Archivo '{rut_a}' no encontrado.")
                with c_a2:
                    v_amb_val = st.slider(f"Volumen: {tit_a}", 0, 100, 40, key=f"vol_amb_db_{id_a}_{idx_a}")
                    volumenes_ambiente.append(v_amb_val / 100.0)
            st.markdown("---")

        # Canales estáticos de respaldo
        c1, c2, c3 = st.columns(3)
        ruta_tormenta = os.path.join("assets", "ambient", "tormenta1.mp3")
        ruta_marron = os.path.join("assets", "ambient", "ruido_marron.mp3")
        ruta_viento = os.path.join("assets", "ambient", "viento.mp3")

        with c1:
            st.markdown("**⚡ Tormenta 1**")
            if os.path.exists(ruta_tormenta):
                st.audio(ruta_tormenta, format="audio/mp3", loop=True)
            else:
                st.error("⚠️ Archivo 'assets/ambient/tormenta1.mp3' no encontrado.")
            vol_tormenta = st.slider("Tormenta", 0, 100, 40, key="vol_tormenta_sleep")

        with c2:
            st.markdown("**☕ Ruido Marrón**")
            if os.path.exists(ruta_marron):
                st.audio(ruta_marron, format="audio/mp3", loop=True)
            else:
                st.error("⚠️ Archivo 'assets/ambient/ruido_marron.mp3' no encontrado.")
            vol_marron = st.slider("Ruido Marrón", 0, 100, 20, key="vol_marron_sleep")

        with c3:
            st.markdown("**🍃 Viento Nocturno**")
            if os.path.exists(ruta_viento):
                st.audio(ruta_viento, format="audio/mp3", loop=True)
            else:
                st.error("⚠️ Archivo 'assets/ambient/viento.mp3' no encontrado.")
            vol_viento = st.slider("Viento", 0, 100, 0, key="vol_viento_sleep")

    # CONTROL JS DE VOLUMEN Y MEDIA SESSION API PARA MODO SUEÑO
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

                // MEDIA SESSION API: Evita el corte de audio en celulares al bloquear pantalla
                if ('mediaSession' in window.parent.navigator) {{
                    window.parent.navigator.mediaSession.metadata = new window.parent.MediaMetadata({{
                        title: 'MAW Player - Sueño',
                        artist: 'Mezclador Activo'
                    }});

                    window.parent.navigator.mediaSession.setActionHandler('play', () => {{
                        audioElements.forEach(aud => aud.play());
                        window.parent.navigator.mediaSession.playbackState = "playing";
                    }});

                    window.parent.navigator.mediaSession.setActionHandler('pause', () => {{
                        audioElements.forEach(aud => aud.pause());
                        window.parent.navigator.mediaSession.playbackState = "paused";
                    }});
                }}
            }}
        }}
        aplicarNivelVolumenes();
        setTimeout(aplicarNivelVolumenes, 500);
        setTimeout(aplicarNivelVolumenes, 1500);
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

    cursor.execute("""
        SELECT id, titulo, ruta_archivo 
        FROM pistas_audio 
        WHERE categoria_id = 'focus' AND tipo_pista = 'ambiente'
    """)
    pistas_focus_amb_db = cursor.fetchall()
    conn.close()

    opciones_focus = {titulo: ruta for id_p, titulo, ruta in pistas_focus_db} if pistas_focus_db else {
        "Lo-Fi Study Beats": os.path.join("assets", "music", "focus_lofi.mp3")
    }

    # REPRODUCTOR FOCUS PRINCIPAL
    with st.container(border=True):
        st.subheader("🎧 Pistas de Enfoque Guardadas")
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
                st.warning(f"⚠️ El archivo no existe en la ruta: '{ruta_focus_actual}'. Regístralo en Administración.")
        with f_col2:
            vol_focus_main = st.slider("Volumen Focus", 0, 100, 80, key="vol_focus_main")

    # MEZCLADOR DE CAPAS AMBIENTALES MULTI-CANAL EN FOCUS
    volumenes_focus_amb = []
    with st.container(border=True):
        st.subheader("🎛️ Capas Ambientales de Fondo para Focus")
        
        if pistas_focus_amb_db:
            st.markdown("### Sonidos de Fondo Registrados")
            for idx_fa, (id_fa, tit_fa, rut_fa) in enumerate(pistas_focus_amb_db):
                fc_a1, fc_a2 = st.columns([2, 3])
                with fc_a1:
                    st.markdown(f"**🔊 {tit_fa}**")
                    if os.path.exists(rut_fa):
                        st.audio(rut_fa, format="audio/mp3", loop=True)
                    else:
                        st.error(f"⚠️ Archivo '{rut_fa}' no encontrado.")
                with fc_a2:
                    v_famb_val = st.slider(f"Volumen: {tit_fa}", 0, 100, 35, key=f"vol_famb_db_{id_fa}_{idx_fa}")
                    volumenes_focus_amb.append(v_famb_val / 100.0)
            st.markdown("---")

        c_f1, c_f2 = st.columns(2)
        ruta_lluvia = os.path.join("assets", "ambient", "lluvia_cafeteria.mp3")
        ruta_binaural = os.path.join("assets", "ambient", "alfa_10hz.mp3")

        with c_f1:
            st.markdown("**☕ Lluvia en Cafetería**")
            if os.path.exists(ruta_lluvia):
                st.audio(ruta_lluvia, format="audio/mp3", loop=True)
            else:
                st.error("⚠️ Archivo 'assets/ambient/lluvia_cafeteria.mp3' no encontrado.")
            vol_lluvia = st.slider("Lluvia/Café", 0, 100, 30, key="vol_lluvia_focus")

        with c_f2:
            st.markdown("**🧠 Ondas Alpha (10 Hz)**")
            if os.path.exists(ruta_binaural):
                st.audio(ruta_binaural, format="audio/mp3", loop=True)
            else:
                st.error("⚠️ Archivo 'assets/ambient/alfa_10hz.mp3' no encontrado.")
            vol_binaural = st.slider("Ondas Alpha", 0, 100, 25, key="vol_binaural_focus")

    # CONTROL JS PARA VOLUMEN Y MEDIA SESSION API PARA MODO FOCUS
    vf_main = vol_focus_main / 100.0
    vf_lluvia = vol_lluvia / 100.0
    vf_binaural = vol_binaural / 100.0

    js_famb_array = str(volumenes_focus_amb)

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
                
                const volsFocusBD = {js_famb_array};
                volsFocusBD.forEach(v => {{
                    if (audioElements[idx]) {{ audioElements[idx].volume = v; idx++; }}
                }});

                if (audioElements[idx]) {{ audioElements[idx].volume = {vf_lluvia}; idx++; }}
                if (audioElements[idx]) {{ audioElements[idx].volume = {vf_binaural}; idx++; }}

                // MEDIA SESSION API: Evita el corte de audio en celulares
                if ('mediaSession' in window.parent.navigator) {{
                    window.parent.navigator.mediaSession.metadata = new window.parent.MediaMetadata({{
                        title: 'MAW Player - Focus',
                        artist: 'Sesión de Productividad'
                    }});

                    window.parent.navigator.mediaSession.setActionHandler('play', () => {{
                        audioElements.forEach(aud => aud.play());
                        window.parent.navigator.mediaSession.playbackState = "playing";
                    }});

                    window.parent.navigator.mediaSession.setActionHandler('pause', () => {{
                        audioElements.forEach(aud => aud.pause());
                        window.parent.navigator.mediaSession.playbackState = "paused";
                    }});
                }}
            }}
        }}
        aplicarAjustesFocus();
        setTimeout(aplicarAjustesFocus, 500);
        setTimeout(aplicarAjustesFocus, 1500);
    </script>
    """
    components.html(js_code_focus, height=0, width=0)

elif "Administración" in modo:
    aplicar_tema_sueno()
    
    st.title("⚙️ Módulo de Administración")
    st.caption("Gestión e ingreso de nuevas pistas de audio con almacenamiento continuo.")

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
                "Título de la Pista (editable):", 
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
                    
                    ruta_guardado = os.path.join(directorio_destino, archivo_audio.name)
                    with open(ruta_guardado, "wb") as f:
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
                    
                    st.success(f"¡Pista '{titulo_pista}' registrada en la base de datos!")
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
                            st.toast(f"Pista '{p_titulo}' eliminada de la base de datos y del disco.")
                            st.rerun()
        else:
            st.info("No hay pistas guardadas actualmente en la base de datos.")
