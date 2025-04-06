from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import pandas as pd
import random
from typing import List, Dict, Text, Any



class ActionPreguntarNombre(Action):
    def name(self) -> Text:
        return "action_preguntar_nombre"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict]:
        dispatcher.utter_message(text="¡Bienvenid@ al recomendador de canciones! 🎶 ¿Cómo te llamas? 🙂")
        return []

class ActionRecomendarMusica(Action):
    def name(self) -> Text:
        return "action_recomendar_musica"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Entidades detectadas en el mensaje actual
        entidades = [ent.get("entity") for ent in tracker.latest_message.get("entities", [])]

        # Reset cruzado de slots si no aparecen en el mensaje actual
        reset_emocion = SlotSet("emocion", None) if "emocion" not in entidades else None
        reset_actividad = SlotSet("actividad", None) if "actividad" not in entidades else None

        # Obtener los valores actualizados (o previos si no se han reseteado aún)
        emocion = tracker.get_slot("emocion") if "emocion" in entidades else None
        actividad = tracker.get_slot("actividad") if "actividad" in entidades else None

        # Cargar base de datos
        try:
            df = pd.read_csv('base_datos_bot_musical.csv')
        except Exception:
            dispatcher.utter_message(text="Hubo un problema al cargar la base de datos de canciones.")
            eventos = [e for e in [reset_emocion, reset_actividad] if e is not None]
            return eventos

        # Filtrar canciones
        canciones_filtradas = pd.DataFrame()
        if emocion:
            canciones_filtradas = df[df['categoria'].str.lower() == emocion.lower()]
        if actividad:
            canciones_filtradas = df[df['categoria'].str.lower() == actividad.lower()]

        # Mensajes según contexto
        if not canciones_filtradas.empty:
            canciones = canciones_filtradas['canción'].dropna().tolist()
            recomendadas = random.sample(canciones, min(5, len(canciones)))

            if emocion == "triste":
                texto = "Te recomiendo estas canciones para acompañar tus días tristes 🌧️:\n"
            elif emocion == "feliz":
                texto = "Te recomiendo estas canciones para cuando tienes un buen día 🎉:\n"
            elif actividad == "entrenar":
                texto = "Te recomiendo estas canciones para animar tus entrenos 🏃‍♀️:\n"
            elif actividad == "estudiar":
                texto = "Te recomiendo estas canciones que te ayudarán a concentrarte 📚:\n"
            elif actividad == "bailar":
                texto = "Te recomiendo estas canciones para bailar 🕺🏻:\n"
            else:
                texto = "Te recomiendo estas canciones:\n"

            texto += "- " + "\n- ".join(recomendadas)
            texto += "\n\n¿Quieres más música? 😊"
            dispatcher.utter_message(text=texto)
        else:
            dispatcher.utter_message(text="Lo siento, no encontré canciones para esa emoción o actividad.")

        # Devolver eventos de limpieza si hace falta
        eventos = [e for e in [reset_emocion, reset_actividad] if e is not None]
        return eventos
    
