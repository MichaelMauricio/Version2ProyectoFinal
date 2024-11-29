import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Configuración inicial de Streamlit
st.set_page_config(page_title="Simulador de Inversiones - Allianz Patrimonial", layout="wide")

# Función para manejar la navegación entre páginas
def navigate_to(page):
    st.session_state["current_page"] = page

# Inicializar la página actual
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "registro"

# Función para descargar datos
@st.cache_data
def download_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)
        if data.empty:
            st.warning(f"No se encontraron datos para el ticker {ticker}.")
        return data
    except Exception as e:
        st.error(f"Error al descargar datos de {ticker}: {e}")
        st.stop()
        return pd.DataFrame()

# Función para calcular rendimientos históricos
def calcular_rendimientos(precios, periodos):
    rendimientos = {}
    for ticker in precios.columns:
        rendimientos[ticker] = {}
        for periodo, dias in periodos.items():
            if len(precios[ticker].dropna()) > dias:
                rendimientos[ticker][periodo] = round(
                    (precios[ticker][-1] / precios[ticker][-dias] - 1) * 100, 2
                )
            else:
                rendimientos[ticker][periodo] = None
    return pd.DataFrame(rendimientos).T

# Sidebar para el monto de inversión y fechas
def sidebar_inversion():
    st.sidebar.header("Configuración de Inversión")
    monto_inversion = st.sidebar.number_input(
        "Monto a Invertir",
        min_value=1000,
        step=100,
        value=10000,
        help="Introduce el monto total que deseas invertir."
    )
    fecha_inicio = st.sidebar.date_input(
        "Fecha de Inicio",
        value=datetime.now() - timedelta(days=365),
        help="Selecciona la fecha de inicio para tu inversión."
    )
    fecha_fin = st.sidebar.date_input(
        "Fecha de Fin",
        value=datetime.now(),
        help="Selecciona la fecha de fin para tu inversión."
    )
    
    if fecha_inicio >= fecha_fin:
        st.sidebar.error("La fecha de inicio debe ser anterior a la fecha de fin.")
    else:
        st.session_state["config_inversion"] = {
            "Monto": monto_inversion,
            "Inicio": fecha_inicio,
            "Fin": fecha_fin
        }
        st.sidebar.success("Configuración de inversión guardada.")

# Página: Registro de Cliente
def registro_cliente():
    st.title("Registro de Cliente")
    st.subheader("Por favor, ingresa tus datos personales para registrarte")

    # Formulario de registro
    nombre = st.text_input("Nombre Completo")
    telefono = st.text_input("Número de Teléfono")
    email = st.text_input("Correo Electrónico")
    ciudad = st.text_input("Ciudad / Estado")
    edad = st.number_input("Edad", min_value=18, max_value=100, step=1)

    acepta_privacidad = st.checkbox("Acepto el Aviso de Privacidad")
    if acepta_privacidad:
        st.write("Al compartir tus datos, confirmas que tienes capacidad legal para contratar y que eres mayor de edad.")

    # Botón para guardar los datos y pasar al cuestionario
    if st.button("Registrar y Continuar"):
        if nombre and telefono and email and ciudad and edad and acepta_privacidad:
            st.session_state["user_data"] = {
                "Nombre": nombre,
                "Teléfono": telefono,
                "Email": email,
                "Ciudad": ciudad,
                "Edad": edad
            }
            st.success(f"Gracias {nombre}, hemos registrado tu información.")
            navigate_to("cuestionario")
        else:
            st.error("Por favor, completa todos los campos antes de continuar.")

# Página: Cuestionario de Perfil de Riesgo
def cuestionario_perfil_riesgo():
    st.title("Cuestionario de Perfil de Riesgo")
    st.subheader("Responde el siguiente cuestionario para evaluar tu tolerancia al riesgo")

    preguntas_secciones = {
        1: [
            "Conozco mis bienes/derechos (activos) y asumo mis deudas/obligaciones (pasivos).",
            "Me enorgullezco del trabajo que realizo y busco aprovechar al máximo los frutos que obtengo de él.",
            "Soy auténtico sin necesidad de quedar bien.",
            "Mi trabajo destaca en mayor medida que el de los demás.",
            "Busco ayuda de los expertos en el tema.",
            "Tomo en cuenta la opinión de los especialistas, sin sesgarme únicamente por esta.",
            "Conozco mis cualidades y me comprometo con mis objetivos.",
            "Sé cuál es mi lugar y evito ser siempre el primero en todo.",
            "Acepto que la especulación puede evidenciar que no estaba en lo correcto.",
            "Cuido mi apariencia sin dedicarle todo el tiempo a ella."
        ],
        2: [
            "Soy adverso a tomar pérdidas, que en mantener las ganancias.",
            "Si asumo más riesgo y llegara a causar pérdidas, mantengo mi posición a largo plazo.",
            "Soy consciente de los ciclos económicos y que a largo plazo el capital tiene una tendencia a crecer.",
            "Compro lo que entiendo y no me importa la opinión ajena.",
            "Mantengo mi posición.",
            "Mantengo mi portafolio a pesar de un VaR (pérdidas máximas en $ esperadas en un portafolio de el 5% de las veces) alto.",
            "Tolero una desviación considerable de mis rendimientos en proporción a la media.",
            "Busco romper el status quo y terminar los plazos de mis portafolios.",
            "Prefiero posponer decisiones de compra/venta esperando un mejor escenario.",
            "Dependo de un margin call o de un piso/techo para tomar una decisión."
        ],
        3: [
            "Soy consciente del riesgo sistémico y actúo de tal manera que puedo conservar por lo menos mi capital a través del tiempo.",
            "Enfrento mi aversión al riesgo sin perder mis metas financieras.",
            "He invertido en un activo a pesar del riesgo relacionado con él.",
            "Tengo experiencias de inversión realizadas por mi cuenta o he acudido con algún intermediario financiero.",
            "Tomas la decisión de una inversión en corto en búsqueda de potencializar tu posible utilidad.",
            "Soy más afecto a tomar pérdidas o a esperar utilidades.",
            "Concuerdo con Peter Lynch: “Solo invierto en lo que entiendo.”",
            "Reconozco mis expectativas, sin perder de vista el costo de oportunidad al que incurro.",
            "Postergó mi decisión de tomar pérdidas o utilidades ante la ansiedad de esperar un mejor escenario.",
            "Reconozco mi aversión al riesgo."
        ],
        4: [
            "Soy ambicioso pero persistente, en lugar de buscar rendimientos cortoplacistas y de riesgo cero.",
            "Me siento cómodo en mi estatus quo y me quedo así.",
            "Soy optimista.",
            "Construyo una imagen de valor, para que un inversionista (compañía o individuo) solicite mi atención.",
            "Tengo impedimentos (familiares, personales, profesionales, de salud, etc.) que me impiden persistir frente a algún pasivo.",
            "Tengo metas altas.",
            "He presentado mis habilidades y aptitudes hacia colegas, para evitar problemas complejos (como la euforia colectiva).",
            "Busco la mayor eficiencia en mis retornos requeridos.",
            "Soy perfeccionista.",
            "Busco la retención de capital a largo plazo en una inversión y cuento con una tasa de rotación de objetivos baja (siendo firme y enfocado en mis compromisos)."
        ],
        5: [
            "Mi capital está trabajando en congruencia con mis necesidades.",
            "Cuento con metas financieras y procuro su cumplimiento en tiempo y forma.",
            "Soy coherente.",
            "Hablo mal a espaldas de las personas.",
            "Cuido la confidencialidad de la información que se me comparte.",
            "A pesar del costo de oportunidad inferido, cumplo mis metas.",
            "Mi riesgo crediticio es alto.",
            "Tengo un código de conducta.",
            "Respeto las reglas y normas establecidas para mi actuación financiera.",
            "¿Me mantengo firme a pesar de la incertidumbre?"
        ],
        6: [
            "Me identifico junto con Warren Buffett al decir: “Tengo miedo cuando los demás son codiciosos.”",
            "Uso la razón para atender mis prioridades y no dejarme llevar por la emoción de los agentes económicos.",
            "Me mantengo ecuánime y flexible ante el riesgo no diversificable.",
            "En presencia de una tendencia determinista y con un nivel de riesgo seleccionado, me alarmo ante una evolución no previsible en la misma desviación estándar (riesgo).",
            "En una posición larga, me agobio ante las obligaciones del corto plazo.",
            "Evito las molestias y agobios ante imprevistos.",
            "Ante un escenario de pérdidas tengo un magical thinking de que mis enemigos son causa del resultado.",
            "Me quejo mucho.",
            "Ante un cambio en el nivel de la media predicho, busco alguna manera de volver a ajustar mi asset allocation model.",
            "Agradezco con facilidad."
        ],
        7: [
            "Llevo registro de las tendencias de mis inversiones para no olvidar su comportamiento histórico.",
            "Amplío mis horizontes de información y trato de evitar el sesgo de anchoring.",
            "Solo invierto en lo que conozco y me encamino a preguntar para ampliar mis horizontes.",
            "Confío en el adagio “Buy the rumor, sell the news.”",
            "No cambio con facilidad de opinión.",
            "No me justifico.",
            "Soy comprometido a pesar de la aleatoriedad de las variables económicas y que, en algunos casos, estas no te generen beneficio."
        ]
    }

     # Manejo de la sección activa actual
    if "seccion_actual" not in st.session_state:
        st.session_state["seccion_actual"] = 1

    # Obtener la sección activa
    seccion_actual = st.session_state["seccion_actual"]

    # Mostrar preguntas de la sección actual
    st.subheader(f"Sección {seccion_actual}")
    respuestas_actuales = {}
    for pregunta in preguntas_secciones[seccion_actual]:
        respuesta = st.radio(
            f"{pregunta}",
            [1, 2, 3, 4],
            key=f"seccion_{seccion_actual}_{pregunta}"
        )
        respuestas_actuales[pregunta] = respuesta

    # Guardar respuestas en el estado
    st.session_state[f"respuestas_seccion_{seccion_actual}"] = respuestas_actuales

    # Botón para continuar a la siguiente sección
    if st.button("Siguiente"):
        # Validar que todas las preguntas fueron respondidas
        if all(respuesta is not None for respuesta in respuestas_actuales.values()):
            if seccion_actual < len(preguntas_secciones):
                st.session_state["seccion_actual"] += 1
            else:
                st.success("Has completado todas las secciones del cuestionario.")
        else:
            st.warning("Por favor, responde todas las preguntas antes de continuar.")

    # Mostrar un mensaje cuando todas las secciones estén completas
    if seccion_actual == len(preguntas_secciones) and all(
        f"respuestas_seccion_{i}" in st.session_state for i in range(1, len(preguntas_secciones) + 1)
    ):
        total_global = sum(
            sum(st.session_state[f"respuestas_seccion_{i}"].values())
            for i in range(1, len(preguntas_secciones) + 1)
        )
        if total_global <= 67:
            nivel_riesgo = "Riesgo Alto"
        elif 68 <= total_global <= 267:
            nivel_riesgo = "Riesgo Medio"
        else:
            nivel_riesgo = "Aversión al Riesgo Baja"

        st.session_state["nivel_riesgo"] = nivel_riesgo
        st.success(f"Tu perfil de riesgo es: {nivel_riesgo}")
        if st.button("Ver Recomendaciones"):
            navigate_to("recomendaciones")

# Página: Recomendaciones de ETFs
# Página: Recomendaciones de ETFs
def recomendaciones_etfs():
    st.title("Recomendaciones de ETFs")
    st.subheader("Basadas en tu perfil de riesgo, te sugerimos las siguientes opciones de inversión")

    recomendaciones = {
        "Riesgo Alto": {
            "ETFs": ["QQQ", "SPY", "EEM"],
            "Distribución": [50, 30, 20]
        },
        "Riesgo Medio": {
            "ETFs": ["VTI", "LQD", "GLD"],
            "Distribución": [40, 40, 20]
        },
        "Aversión al Riesgo Baja": {
            "ETFs": ["BND", "BNDX", "VDC"],
            "Distribución": [20, 60, 20]
        }
    }

    nombres_etfs = {
        "QQQ": "Invesco QQQ Trust (Tecnología, Nasdaq-100)",
        "SPY": "SPDR S&P 500 ETF Trust (Acciones del S&P 500)",
        "EEM": "iShares MSCI Emerging Markets ETF (Mercados Emergentes)",
        "VTI": "Vanguard Total Stock Market ETF (Mercado Total de EE. UU.)",
        "LQD": "iShares iBoxx $ Investment Grade Corporate Bond ETF (Bonos Corporativos)",
        "GLD": "SPDR Gold Shares (Oro)",
        "BND": "Vanguard Total Bond Market ETF (Bonos de EE. UU.)",
        "BNDX": "Vanguard Total International Bond ETF (Bonos Internacionales)",
        "VDC": "Vanguard Consumer Staples ETF (Consumo Básico)"
    }

    explicaciones_perfil = {
        "Riesgo Alto": "Seleccionamos ETFs como QQQ, SPY y EEM que se enfocan en sectores con alto potencial de crecimiento "
                       "(tecnología, mercados emergentes y el S&P 500). Estos instrumentos tienden a ser más volátiles, "
                       "pero ofrecen mayores rendimientos a largo plazo.",
        "Riesgo Medio": "Seleccionamos ETFs como VTI, LQD y GLD que diversifican entre acciones generales de mercado, "
                        "bonos corporativos y oro. Esta combinación busca equilibrio entre riesgo y rendimiento.",
        "Aversión al Riesgo Baja": "Seleccionamos ETFs como BND, BNDX y VDC que priorizan la estabilidad y la protección del capital. "
                                   "Estos instrumentos incluyen bonos estadounidenses, internacionales y sectores defensivos."
    }

    nivel_riesgo = st.session_state.get("nivel_riesgo", None)
    if nivel_riesgo in recomendaciones:
        # Mostrar los ETFs recomendados
        st.success(f"Tu perfil de riesgo es: {nivel_riesgo}")
        etfs = recomendaciones[nivel_riesgo]["ETFs"]
        distribucion_default = recomendaciones[nivel_riesgo]["Distribución"]

        # Inicializar asignaciones
        if "asignaciones" not in st.session_state:
            st.session_state.asignaciones = {etf: dist for etf, dist in zip(etfs, distribucion_default)}

        # Mostrar explicación del perfil de riesgo en la barra lateral
        st.sidebar.header("Perfil de Riesgo")
        st.sidebar.info(explicaciones_perfil[nivel_riesgo])

        # Ajustar porcentajes
        st.write("### Ajusta el porcentaje de tu inversión a cada ETF:")
        for etf in etfs:
            st.session_state.asignaciones[etf] = st.slider(
        f"{etf} - {nombres_etfs[etf]}:",
        min_value=0,
        max_value=100,
        value=st.session_state.asignaciones[etf],
        step=1
    )


        # Validar que la suma sea igual a 100%
        suma_porcentajes = sum(st.session_state.asignaciones.values())
        if suma_porcentajes != 100:
            st.error("La suma de las asignaciones debe ser igual al 100%. Ajusta los porcentajes.")
            return

        pesos = [st.session_state.asignaciones[etf] / 100 for etf in etfs]

        # Descargar datos para los ETFs seleccionados
        start_date = st.date_input("Fecha de inicio", datetime.now() - timedelta(days=365 * 10))
        end_date = st.date_input("Fecha de fin", datetime.now())
        precios = pd.DataFrame()
        for etf in etfs:
            data = download_data(etf, start_date, end_date)
            precios[etf] = data["Close"]

        # Gráfica de desempeño comparativo
        st.subheader("Desempeño Comparativo de los ETFs Recomendados")
        precios_normalizados = precios / precios.iloc[0] * 1000
        st.line_chart(precios_normalizados, use_container_width=True)

        # Cálculo del rendimiento esperado y volatilidad
        daily_returns = precios.pct_change().dropna()
        rendimiento_anual = daily_returns.mean() * 252
        matriz_covarianza = daily_returns.cov() * 252

        rendimiento_esperado = np.dot(pesos, rendimiento_anual) * 100
        volatilidad_cartera = np.sqrt(np.dot(pesos, np.dot(matriz_covarianza, pesos))) * 100

        st.write("### Resultados de la simulación de cartera:")
        st.write(f"- Rendimiento esperado: {rendimiento_esperado:.2f}%")
        st.write(f"- Volatilidad de la cartera: {volatilidad_cartera:.2f}%")

        # Guardar rendimiento esperado en el estado
        st.session_state["expected_return"] = rendimiento_esperado

        # Gráfico del rendimiento histórico de la cartera
        precios_normalizados = precios / precios.iloc[0]
        rendimiento_cartera = (precios_normalizados * pesos).sum(axis=1)

        st.subheader("Rendimiento Histórico de la Cartera")
        st.line_chart(rendimiento_cartera, use_container_width=True)

    else:
        st.warning("Completa el cuestionario para recibir recomendaciones.")
    if st.button("Ir a la Calculadora de Interés Compuesto"):
        navigate_to("calculadora")
    # Página: Calculadora de Interés Compuesto
def calculadora_interes_compuesto():
    st.title("Calculadora de Interés Compuesto")
    st.subheader("Simula el crecimiento de tu inversión basada en el rendimiento esperado de la cartera")

    # Obtener el rendimiento esperado desde el estado de sesión
    rendimiento_esperado = st.session_state.get("expected_return", None)

    if rendimiento_esperado is not None:
        # Mostrar el rendimiento esperado
        st.info(f"El rendimiento esperado anual utilizado para la simulación es: {rendimiento_esperado:.2f}%")

        # Entradas del simulador (en la misma página)
        aportacion_inicial = st.number_input(
            "Aportación inicial",
            min_value=0,
            value=1000,
            step=100,
            help="Monto inicial que deseas invertir."
        )
        aportacion_periodica = st.number_input(
            "Aportación periódica (mensual)",
            min_value=0,
            value=100,
            step=10,
            help="Monto que planeas invertir mensualmente."
        )
        horizonte_inversion = st.slider(
            "Horizonte de inversión (años)",
            min_value=1,
            max_value=30,
            value=5,
            step=1,
            help="Duración total de la inversión en años."
        )

        # Simulación de interés compuesto
        num_aportaciones_anuales = 12  # Frecuencia mensual fija
        tasa_aportacion = (1 + (rendimiento_esperado / 100)) ** (1 / num_aportaciones_anuales) - 1

        # Inicializar los valores de inversión y ahorro
        patrimonio_inversion = [aportacion_inicial]
        patrimonio_ahorro = [aportacion_inicial]

        for _ in range(horizonte_inversion * num_aportaciones_anuales):
            # Cálculo con interés compuesto
            nuevo_valor_inversion = patrimonio_inversion[-1] + aportacion_periodica
            nuevo_valor_inversion *= (1 + tasa_aportacion)
            patrimonio_inversion.append(nuevo_valor_inversion)

            # Cálculo sin interés (ahorro simple)
            patrimonio_ahorro.append(patrimonio_ahorro[-1] + aportacion_periodica)

        # Crear un DataFrame para los datos de la gráfica
        inversion_df = pd.DataFrame({
            "Inversión con Rendimiento": patrimonio_inversion,
            "Ahorro sin Rendimiento": patrimonio_ahorro
        })

        # Mostrar gráfico
        st.subheader("Crecimiento de tu inversión a lo largo del tiempo")
        st.line_chart(inversion_df)

        # Mostrar resultados finales
        valor_final_inversion = patrimonio_inversion[-1]
        valor_final_ahorro = patrimonio_ahorro[-1]

        st.markdown(
            f"<h3 style='text-align: center; color: #4CAF50;'>"
            f"Valor final estimado de la inversión después de {horizonte_inversion} años: ${valor_final_inversion:,.2f}"
            f"</h3>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<h3 style='text-align: center; color: #FF5722;'>"
            f"Valor acumulado sin rendimiento después de {horizonte_inversion} años: ${valor_final_ahorro:,.2f}"
            f"</h3>",
            unsafe_allow_html=True
        )
    else:
        st.warning("Por favor, completa la configuración de inversión y cálculo de rendimiento esperado antes de usar esta herramienta.")


# Navegación entre páginas
# Bloque de navegación
if st.session_state["current_page"] == "registro":
    registro_cliente()
elif st.session_state["current_page"] == "cuestionario":
    cuestionario_perfil_riesgo()
elif st.session_state["current_page"] == "recomendaciones":
    recomendaciones_etfs()
elif st.session_state["current_page"] == "calculadora":
    calculadora_interes_compuesto()

