import streamlit as st
from abc import ABC, abstractmethod
from typing import Callable, Any, Dict
import pandas as pd
from datetime import datetime
import random

class GameController:
    """
    Gestiona el estado global de la gamificación.
    """
    def __new__(cls, *args, **kwargs):
        if 'GameController' in st.session_state:
            return st.session_state.GameController
        instance = super().__new__(cls)
        return instance

    def __init__(self, translation: Dict[str, str] | None = None):
        self.t = translation or {}
        if hasattr(self, 'game_mode'): return
        
        self.registered_games: Dict[str, 'Minigame'] = {}
        st.session_state.GameController = self
        
        self.game_mode = True
        if 'game_mode_toggle_state' not in st.session_state:
            st.session_state.game_mode_toggle_state = self.game_mode

        self.show_confirm_dialog = False
        

    def _full_reset(self):
        for game in self.registered_games.values():
            game.reset_game()

    def switch_off(self)-> None:
        self.game_mode = False
        st.session_state.game_mode_toggle_state = False
    
    def switch_on(self) -> None:
        if self.game_mode is False:
            st.session_state.game_mode_toggle_state = False
            self.game_mode = True
            

    def _handle_toggle_change(self, show_confirm_dialog:bool = True):
        """
        Esta funcion se ejecuta cuando se hace clic en el toggle y decide si cambiar el estado directamente o si mostrar un dialogo de confirmación.
        """
        widget_state = st.session_state.game_mode_toggle_state

        if widget_state is True and self.game_mode is False:
            self.game_mode = True
            self._full_reset()

        elif widget_state is False and self.game_mode is True:
            self.show_confirm_dialog = show_confirm_dialog
            st.session_state.game_mode_toggle_state = True

    def _show_confirmation_dialog(self):
        if self.show_confirm_dialog:
            self.show_confirm_dialog = False
            @st.dialog(self.t.get('confirm_deactivation_title', "Confirmar Desactivación"))
            def show_confirmation_dialog():
                st.warning(self.t.get('confirm_deactivation_warning', "¿Seguro que quieres desactivar el Modo Juego?"), icon="🤔")
                st.write(self.t.get('confirm_deactivation_text', "Dejarás de ver los minijuegos interactivos y perderás tu progreso actual."))
                c1, c2 = st.columns(2)
                if c1.button(self.t.get('confirm_button', "Confirmar"), use_container_width=True, type="primary"):
                    self.switch_off()
                    st.rerun()
                if c2.button(self.t.get('cancel_button', "Cancelar"), use_container_width=True):
                    st.rerun()
            show_confirmation_dialog()

    def display_mode_toggle(self):
        self._show_confirmation_dialog()
        st.toggle(
            self.t.get('game_mode_label', '**Modo Juego**'),
            key='game_mode_toggle_state',
            value=self.game_mode,
            on_change=self._handle_toggle_change,
            help=self.t.get('toggle_help', "Activa/desactiva los minijuegos interactivos.")
        )

    def display_score_panel(self):
        if not self.game_mode: return
        st.header(self.t.get('progress_header', "🏆 Tu Progreso"))
        if st.button(self.t.get('reset_progress_button', "Reiniciar Progreso"), use_container_width=True, type="secondary"):
            self._full_reset()
            st.rerun()
        
        total_score, completed_games = 0, [g for g in self.registered_games.values() if g.is_finished()]
        for game in completed_games: total_score += game.get_result()[0]
        
        c1, c2 = st.columns(2)
        c1.metric(self.t.get('points_metric_label', "Puntos"), total_score)
        c2.metric(self.t.get('games_metric_label', "Juegos"), len(completed_games))
        
        with st.expander(self.t.get('history_expander_label', "Ver Historial de Partidas")):
            sortable_games = [g for g in completed_games if g.completion_time]
            if not sortable_games:
                st.caption(self.t.get('history_empty', "Aún no has jugado. ¡Anímate!"))
            else:
                for game in sorted(sortable_games, key=lambda g: g.completion_time, reverse=True): # type: ignore
                    points_earned, was_successful = game.get_result()
                    icon = "✅" if was_successful else "❌"
                    text = self.t.get('history_item_text', "{icon} **{game_title}**: *+{points_earned} pts*").format(icon=icon, game_title=game.game_title, points_earned=points_earned)
                    st.markdown(text)
    
    def display_debug_panel(self):
        """Muestra el panel con el estado interno de todos los juegos registrados."""
        with st.expander("🛠️ Panel de Depuración del Motor de Juegos", expanded=False):
            if not self.registered_games:
                st.caption("No hay juegos registrados.")
                return
            
            game_states = []
            for game_id, game in self.registered_games.items():
                game_states.append({
                    "ID": game_id,
                    "Clase": type(game).__name__,
                    "Finalizado": "✅" if game.is_finished() else "❌",
                    "Ronda": f"{game.current_round}/{game.num_rounds}",
                    "Puntos": game.total_score,
                    "Datos Ronda": len(game.rounds_data),
                })
            st.dataframe(pd.DataFrame(game_states), use_container_width=True)


class Minigame(ABC):
    def __new__(cls, game_id: str, **kwargs):
        if 'GameController' not in st.session_state: raise Exception('GameController must be initialized before any Minigame.')
        controller = st.session_state.GameController
        if game_id in controller.registered_games: return controller.registered_games[game_id]
        instance = super().__new__(cls)
        return instance

    def __init__(self, game_id: str, game_title: str, data: pd.DataFrame | None = None, content_callback: Callable | None = None, num_rounds: int = 1, translation:dict={}, min_score_for_victory:int|None=None):
        self.t = st.session_state.GameController.t.get(self.__class__.__name__, {}) | translation
        if hasattr(self, 'game_id'): return
        self.game_id = game_id
        self.game_title = game_title
        self.controller = st.session_state.GameController
        
        self.data = data
        self.content_callback: Callable|None = content_callback
        self.min_score_for_victory = min_score_for_victory
        
        if self.data is not None:
            self.num_rounds = min(num_rounds, len(self.data)) if num_rounds > 0 else len(self.data)
        else:
            self.num_rounds = num_rounds

        self.reset_game()
        self.controller.registered_games[self.game_id] = self

    def reset_game(self):
        self.current_round: int = 0
        self.round_results: list[dict] = []
        self.total_score: int = 0
        self.completion_time: datetime | None = None
        self.rounds_data: list[Any] = []

    def is_finished(self) -> bool: return self.completion_time is not None
    
    def get_result(self) -> tuple[int, bool]:
        if not self.is_finished(): return 0, False
        was_successful = any(r.get('was_correct', False) for r in self.round_results)
        return self.total_score, was_successful

    def _process_submission(self, user_answer, round_data):
        score, was_correct = self.calculate_score(user_answer, round_data)
        self.round_results.append({"score": score, "was_correct": was_correct, "user_answer": user_answer, "round_data": round_data})
        self.total_score += score
        self.current_round += 1
        if self.current_round >= self.num_rounds: self.completion_time = datetime.now()
        st.rerun()

    def _display_post_game_content(self):
        st.markdown("---")
        st.subheader(self.t.get('detailed_analysis_revealed', "Análisis Detallado Revelado"))
        if self.content_callback: self.content_callback()
    
    def render(self) -> bool:
        if self.content_callback is None:
            if not self.controller.game_mode: return True
            if self.is_finished(): self.display_feedback(); return True
        else:
            if not self.controller.game_mode: self.content_callback(); return True
            if self.is_finished(): self.display_feedback(); self._display_post_game_content(); return True
        self._render_active_game(); return False

    def _render_active_game(self):
        self.display_instructions()
        if self.num_rounds > 1: st.info(f"{self.t.get('round', 'Ronda')} {self.current_round + 1} / {self.num_rounds}", icon="🚩")
        if len(self.rounds_data) <= self.current_round:
            self.rounds_data.append(self.prepare_round_data(self.current_round))
        self._render_submission_ui(self.rounds_data[self.current_round])

    def display_feedback(self):
        if self.min_score_for_victory is not None:
            if self.total_score >= self.min_score_for_victory:
                victory_text = self.t.get('feedback_victory', "¡Victoria! Has superado el desafío con **{total_score}** puntos.")
                st.success(victory_text.format(total_score=self.total_score), icon="🏆")
            else:
                defeat_text = self.t.get('feedback_defeat', "¡Casi! Has obtenido **{total_score}** puntos. ¡Inténtalo de nuevo!")
                st.warning(defeat_text.format(total_score=self.total_score), icon="💪")
        else:
            default_text = self.t.get('feedback_game_over_text', "Has obtenido un total de **{total_score}** puntos.")
            st.success(default_text.format(total_score=self.total_score), icon="🎉")

        if self.num_rounds > 0 and self.round_results:
            with st.expander(self.t.get('see_round_summary', "Ver resumen detallado de rondas")):
                for i, result in enumerate(self.round_results): self.display_round_feedback(result, i + 1)

    def _render_submission_ui(self, round_data: Any):
        with st.form(key=f"form_{self.game_id}_{self.current_round}"):
            user_answer = self.display_game_body(round_data)
            submit_label = self.t.get('submit_button_label', "¡Comprobar!")
            if st.form_submit_button(submit_label, use_container_width=True, type="primary"):
                if user_answer is not None: self._process_submission(user_answer, round_data)
                else: st.warning(self.t.get('please_pick_an_action',"Por favor, realiza una acción antes de comprobar."))

    @abstractmethod
    def display_instructions(self): pass
    @abstractmethod
    def display_game_body(self, round_data: Any) -> Any: pass
    @abstractmethod
    def calculate_score(self, user_answer: Any, round_data: Any) -> tuple[int, bool]: pass
    @abstractmethod
    def display_round_feedback(self, round_result: dict, round_number: int): pass
    @abstractmethod
    def prepare_round_data(self, round_index: int) -> Any: pass

class RowBasedMinigame(Minigame):
    """
    Una clase base para minijuegos que procesan un DataFrame fila por fila en orden aleatorio.
    Maneja el barajado de datos automáticamente.
    """
    def reset_game(self):
        super().reset_game()
        if self.data is not None:
            self.shuffled_indices = random.sample(range(len(self.data)), len(self.data))

    def prepare_round_data(self, round_index: int) -> pd.Series:
        """
        Obtiene la fila de datos para la ronda actual usando el índice barajado.
        """
        if self.data is None or not hasattr(self, 'shuffled_indices'):
            raise ValueError("RowBasedMinigame requiere un DataFrame, si ve este error por favor reportelo en el menú de atención al cliente.")
        return self.data.iloc[self.shuffled_indices[round_index]]