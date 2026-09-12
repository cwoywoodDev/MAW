import streamlit as st

def aplicar_tema_sueno():
    st.markdown("""
    <style>
        #MainMenu, footer, header { visibility: hidden; }

        /* Ocultar opciones de tres puntos y descargas en reproductores nativos */
        audio::-webkit-media-controls-overflow-button,
        audio::-webkit-media-controls-overflow-menu-list,
        audio::-webkit-media-controls-overflow-menu-list-item,
        audio::-webkit-media-controls-download-button,
        audio::-webkit-media-controls-volume-control-container,
        audio::-webkit-media-controls-volume-slider,
        audio::-webkit-media-controls-mute-button {
            display: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
            width: 0 !important;
            height: 0 !important;
        }

        audio::-webkit-media-controls-enclosure {
            overflow: hidden !important;
        }

        audio::-internal-media-controls-overflow-button {
            display: none !important;
        }

        audio {
            width: 100% !important;
            height: 40px !important;
            border-radius: 8px !important;
            filter: invert(85%) hue-rotate(180deg) !important;
            outline: none !important;
        }

        /* PALETA MODO SUEÑO (#2E1D2F) */
        .stApp {
            background-color: #2E1D2F !important;
            color: #B7BACD !important;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #523249 !important;
            border: 1px solid #87B99C !important;
            border-radius: 16px !important;
            box-shadow: 0 10px 25px rgba(46, 29, 47, 0.7) !important;
        }

        div.stButton > button {
            background: linear-gradient(135deg, #523249 0%, #2E1D2F 100%) !important;
            color: #A4C9C8 !important;
            border: 1px solid #87B99C !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
        }

        div.stButton > button:hover {
            background: #87B99C !important;
            color: #2E1D2F !important;
            border-color: #A4C9C8 !important;
            box-shadow: 0 0 15px rgba(135, 185, 156, 0.5) !important;
        }

        div[data-baseweb="slider"] div {
            background-color: #87B99C !important;
        }
        
        div[role="slider"] {
            background-color: #A4C9C8 !important;
            border: 2px solid #2E1D2F !important;
        }

        h1, h2, h3 {
            color: #A4C9C8 !important;
            letter-spacing: 1.2px;
        }

        .stCaption, p, label {
            color: #B7BACD !important;
        }
    </style>
    """, unsafe_allow_html=True)

def aplicar_tema_focus():
    st.markdown("""
    <style>
        #MainMenu, footer, header { visibility: hidden; }

        audio::-webkit-media-controls-overflow-button,
        audio::-webkit-media-controls-overflow-menu-list,
        audio::-webkit-media-controls-overflow-menu-list-item,
        audio::-webkit-media-controls-download-button,
        audio::-webkit-media-controls-volume-control-container,
        audio::-webkit-media-controls-volume-slider,
        audio::-webkit-media-controls-mute-button {
            display: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
            width: 0 !important;
            height: 0 !important;
        }

        audio::-webkit-media-controls-enclosure {
            overflow: hidden !important;
        }

        audio::-internal-media-controls-overflow-button {
            display: none !important;
        }

        audio {
            width: 100% !important;
            height: 40px !important;
            border-radius: 8px !important;
            filter: invert(80%) hue-rotate(90deg) !important;
            outline: none !important;
        }

        /* PALETA MODO FOCUS (#2E1D2F / #523249 / #87B99C / #A4C9C8) */
        .stApp {
            background-color: #2E1D2F !important;
            color: #B7BACD !important;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #523249 !important;
            border: 1px solid #87B99C !important;
            border-radius: 16px !important;
            box-shadow: 0 10px 25px rgba(46, 29, 47, 0.7) !important;
        }

        div.stButton > button {
            background: linear-gradient(135deg, #87B99C 0%, #523249 100%) !important;
            color: #2E1D2F !important;
            border: 1px solid #A4C9C8 !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
        }

        div.stButton > button:hover {
            background: #A4C9C8 !important;
            color: #2E1D2F !important;
            border-color: #87B99C !important;
            box-shadow: 0 0 15px rgba(164, 201, 200, 0.6) !important;
        }

        div[data-baseweb="slider"] div {
            background-color: #87B99C !important;
        }
        
        div[role="slider"] {
            background-color: #A4C9C8 !important;
            border: 2px solid #2E1D2F !important;
        }

        h1, h2, h3 {
            color: #A4C9C8 !important;
            letter-spacing: 1.2px;
        }

        .stCaption, p, label {
            color: #B7BACD !important;
        }
    </style>
    """, unsafe_allow_html=True)