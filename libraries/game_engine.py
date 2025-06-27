import streamlit as st
from abc import ABC, abstractmethod
from typing import Callable, Any, Dict
import pandas as pd
from datetime import datetime

class GameController:
    """
    Gestiona el estado global de la gamificación.
    Versión 9.0: Arquitectura de renderizado híbrida (Convención sobre Configuración).
    """
    def __init__(self, translation: Dict[str, str] | None = None):
        self.t = translation or {}
        if 'GameData' not in st.session_state:
            st.session_state.GameData = {"game_mode": True, "registered_games": {}}
        if 'game_mode_toggle_state' not in st.session_state:
            st.session_state.game_mode_toggle_state = True
        st.session_state.GameController = self

    def get_registered_games(self) -> Dict[str, 'Minigame']:
        return st.session_state.GameData.get('registered_games', {})

    def _full_reset(self):
        for game in self.get_registered_games().values(): game.reset_game()
    
    def manage_state_and_dialogs(self):
        logical_mode = st.session_state.GameData['game_mode']
        widget_mode = st.session_state.game_mode_toggle_state
        if logical_mode == widget_mode: return

        if widget_mode is True:
            st.session_state.GameData['game_mode'] = True
            self._full_reset()
            st.rerun()
        else:
            @st.dialog(self.t.get('confirm_deactivation_title', "Confirmar Desactivación"))
            def show_confirmation_dialog():
                st.warning(self.t.get('confirm_deactivation_warning', "¿Seguro que quieres desactivar el Modo Juego?"), icon="🤔")
                st.write(self.t.get('confirm_deactivation_text', "Dejarás de ver los minijuegos interactivos y perderás tu progreso actual."))
                c1, c2 = st.columns(2)
                if c1.button(self.t.get('confirm_button', "Confirmar"), use_container_width=True, type="primary"): self._deactivate_game_mode()
                if c2.button(self.t.get('cancel_button', "Cancelar"), use_container_width=True):
                    st.session_state.game_mode_toggle_state = True
                    st.rerun()
            show_confirmation_dialog()

    def _deactivate_game_mode(self):
        st.session_state.GameData['game_mode'] = False
        st.session_state.game_mode_toggle_state = False
        st.rerun()
    
    def _handle_mode_change(self):
        st.session_state.game_mode_toggle_state = st.session_state.get('game_mode_toggle_widget', True)
        self.manage_state_and_dialogs()

    def display_mode_toggle(self):
        """Muestra el toggle para activar/desactivar el modo juego. Debe llamarse dentro de un contenedor (ej. st.sidebar)."""
        st.toggle(self.t.get('game_mode_label', '**Modo Juego**'), key="game_mode_toggle_widget", value=st.session_state.game_mode_toggle_state, on_change=self._handle_mode_change, help=self.t.get('toggle_help', "Activa/desactiva los minijuegos interactivos."))

    def display_score_panel(self):
        """Muestra el panel de puntuación. Debe llamarse dentro de un contenedor (ej. st.sidebar)."""
        if not st.session_state.GameData.get('game_mode', False): return
        st.header(self.t.get('progress_header', "🏆 Tu Progreso"))
        if st.button(self.t.get('reset_progress_button', "Reiniciar Progreso"), use_container_width=True, type="secondary"):
            self._full_reset()
            st.rerun()
        total_score = 0
        completed_games = [g for g in self.get_registered_games().values() if g.is_completed()]
        for game in completed_games:
            points, _ = game.get_final_result()
            total_score += points
        c1, c2 = st.columns(2)
        c1.metric(self.t.get('points_metric_label', "Puntos"), total_score)
        c2.metric(self.t.get('games_metric_label', "Juegos"), len(completed_games))
        with st.expander(self.t.get('history_expander_label', "Ver Historial de Partidas")):
            if not completed_games:
                st.caption(self.t.get('history_empty', "Aún no has jugado. ¡Anímate!"))
            else:
                for game in sorted(completed_games, key=lambda g: g.completion_time, reverse=True):
                    points_earned, was_correct = game.get_final_result()
                    icon = "✅" if was_correct else "❌"
                    text = self.t.get('history_item_text', "{icon} **{game_title}**: *+{points_earned} pts*").format(icon=icon, game_title=game.game_title, points_earned=points_earned)
                    st.markdown(text)

class Minigame(ABC):
    def __new__(cls, game_id: str, **kwargs):
        if 'GameController' not in st.session_state: raise Exception('GameController must be initialized before any Minigame.')
        controller = st.session_state.GameController
        registered_games = controller.get_registered_games()
        if game_id in registered_games: return registered_games[game_id]
        instance = super().__new__(cls)
        return instance

    def __init__(self, game_id: str, game_title: str, data: pd.DataFrame, content_callback: Callable | None = None, num_rounds: int = 1, translation:dict={}):
        if hasattr(self, '_initialized'): return
        self.game_id = game_id
        self.game_title = game_title
        self.controller = st.session_state.GameController
        self.t = translation
        self.data = data
        self.content_callback = content_callback
        self.num_rounds = min(num_rounds, len(data)) if num_rounds > 0 else 1
        self.state_key = f"game_state_{self.game_id}"
        self.completion_time: datetime | None = None
        self.controller.get_registered_games()[self.game_id] = self
        self.reset_game()
        self._initialized = True

    def reset_game(self):
        st.session_state[self.state_key] = {"current_round": 0, "game_over": False, "round_results": [], "total_score": 0, "current_round_context": None}
        self.completion_time = None

    def is_completed(self) -> bool:
        return st.session_state[self.state_key].get('game_over', False)

    def get_final_result(self) -> tuple[int, bool]:
        if not self.is_completed(): return 0, False
        state = st.session_state[self.state_key]
        total_score = state.get('total_score', 0)
        was_successful = any(r.get('was_correct', False) for r in state.get('round_results', []))
        return total_score, was_successful

    def _process_submission(self, user_answer, round_data):
        state = st.session_state[self.state_key]
        score, was_correct = self.calculate_score(user_answer, round_data)
        state['round_results'].append({"score": score, "was_correct": was_correct, "user_answer": user_answer, "round_data": round_data})
        state['total_score'] += score
        state['current_round'] += 1
        state['current_round_context'] = None
        if state['current_round'] >= self.num_rounds:
            state['game_over'] = True
            self.completion_time = datetime.now()
        st.rerun()

    def _display_post_game_content(self):
        """Muestra el contenido post-juego. Llamado solo en el 'modo automático' (con callback)."""
        st.markdown("---")
        st.subheader(self.t.get('detailed_analysis_revealed', "Análisis Detallado Revelado"))
        self.content_callback()
    
    def render(self) -> bool:
        """
        Renderiza el minijuego y gestiona su ciclo de vida.
        - Si se proporciona `content_callback` (modo automático): gestiona todo el flujo y no devuelve nada útil.
        - Si `content_callback` es None (modo manual): devuelve `True` si el juego ha terminado, `False` si sigue activo.
        """
        if self.content_callback is None:
            if not st.session_state.GameData.get('game_mode', False):
                return True # Si no hay modo juego, se considera "terminado" para mostrar el contenido.

            if self.is_completed():
                self.display_feedback()
                return True
            else:
                self._render_active_game()
                return False
        
        else:
            if not st.session_state.GameData.get('game_mode', False):
                self.content_callback()
                return True # Devuelve True por consistencia, aunque no se use.

            if self.is_completed():
                self.display_feedback()
                self._display_post_game_content()
                return True
            else:
                self._render_active_game()
                return False

    def _render_active_game(self):
        """Lógica interna para renderizar un juego que está en curso."""
        self.display_instructions()
        state = st.session_state[self.state_key]
        if self.num_rounds > 1:
            st.info(f"{self.t.get('round', 'Ronda')} {state['current_round'] + 1} / {self.num_rounds}", icon="🚩")
        if state.get('current_round_context') is None:
            state['current_round_context'] = self.prepare_round_data(state['current_round'])
            st.rerun()
        round_data = state['current_round_context']
        self._render_submission_ui(round_data)

    @abstractmethod
    def display_instructions(self): pass
    @abstractmethod
    def display_game_body(self, round_data: Any): pass
    @abstractmethod
    def calculate_score(self, user_answer, round_data: Any) -> tuple[int, bool]: pass
    @abstractmethod
    def display_round_feedback(self, round_result: dict, round_number: int): pass
    @abstractmethod
    def prepare_round_data(self, round_index: int) -> Any: pass
    
    def display_feedback(self):
        state = st.session_state[self.state_key]
        st.success(self.t.get('feedback_game_over_text', "Has obtenido un total de **{total_score}** puntos.").format(total_score=state['total_score']), icon="🎉")
        if self.num_rounds > 1:
            with st.expander(self.t.get('see_round_summary', "Ver resumen detallado de rondas")):
                for i, result in enumerate(state['round_results']):
                    self.display_round_feedback(result, i + 1)
                    
    def _render_submission_ui(self, round_data: Any):
        with st.form(key=f"form_{self.game_id}_{st.session_state[self.state_key]['current_round']}"):
            user_answer = self.display_game_body(round_data)
            submit_label = self.t.get('submit_button_label', "¡Comprobar!")
            if st.form_submit_button(submit_label, use_container_width=True):
                self._process_submission(user_answer, round_data)