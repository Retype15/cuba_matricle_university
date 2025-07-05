from typing import Literal, LiteralString
import streamlit as st
import re

class StylableContainer:
    """
    A Streamlit container component designed to apply isolated CSS styles.

    This class provides a context manager for `st.container()`, enabling
    the application of specific CSS rules without affecting other elements
    on the Streamlit page. It injects a unique HTML marker within its
    internal container and uses a precise CSS selector for isolation.

    Usage Example:
        custom_css = '''
        {selector} h3 {
            color: purple;
        }
        '''
        with StylableContainer(key="my_custom_container", css=custom_css):
            st.subheader("This heading is purple and styled.")
            st.write("Any Streamlit element placed within this block will be subject to the defined CSS.")

    Args:
        key (str): A unique string identifier for the container instance.
                   This is crucial for distinct styling when multiple
                   `StylableContainer` instances are used on the same page.
        css (str): The CSS string to be applied. It must include the
                   '{selector}' placeholder, which will be dynamically
                   replaced with a unique, isolated CSS selector targeting
                   elements within this specific container.
    """
    def __init__(self, key: str, css: str, target: Literal['main','sidebar'] = 'main'):
        self.key = key
        self.target = target

        if self.target not in ['main', 'sidebar']:
            raise ValueError("Target must be either 'main' or 'sidebar'.")

        if self.target == 'sidebar':
            self._container = st.sidebar
        else:
            self._container = st.container()

        self.css = self._validate_css(css)

    def _validate_css(self, css: str) -> str:
        """
        Validates the provided CSS string for security and prepares it by
        inserting the unique container selector.

        Raises:
            ValueError: If the CSS string contains disallowed '<script>' tags.
        """
        if re.search(r"<script", css, re.IGNORECASE):
            raise ValueError("Provided CSS cannot contain '<script>' tags.")
        
        if self.target == 'sidebar':
            specific_selector = f'section[data-testid="stSidebar"]:has(div#marker-{self.key})'
        else:
            specific_selector = (
                f'div[data-testid="stVerticalBlock"] '
                f'div[data-testid="stVerticalBlock"]:has(div#marker-{self.key})'
            )

        return f"<style>{css.format(selector=specific_selector)}</style>"

    def __enter__(self):
        """
        Enters the context manager block.
        Injects a hidden HTML marker into the internal container and applies
        the prepared CSS to the Streamlit app. It then activates the context
        of the internal `st.container`.
        """
        container_to_mark = self._container if self.target == 'main' else st.sidebar
        container_to_mark.markdown(f'<div id="marker-{self.key}" style="display: none;"></div>', unsafe_allow_html=True)
        
        st.markdown(self.css, unsafe_allow_html=True)
        
        self._container.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the context manager block.
        Deactivates the context of the internal `st.container`.
        """
        self._container.__exit__(exc_type, exc_val, exc_tb)


# --- CSS DEFINITIONS ---
RADIO_BUTTON_CSS = """
{selector} [data-testid="stRadio"] label:not([data-testid="stWidgetLabel"]) > div:first-child {{
    display: none;
}}
{selector} [data-testid="stRadio"] label:not([data-testid="stWidgetLabel"]) {{
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #262730;
    border: 2px solid #262730;
    border-radius: 0.75rem;
    padding: 0.5rem 1rem;
    margin-bottom: 0.5rem;
    #margin-right: 0.5rem;
    width: 100%;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
}}
{selector} [data-testid="stRadio"] label:not([data-testid="stWidgetLabel"]):hover {{
    background-color: #31333f;
    border-color: #ff4b4b;
}}
{selector} [data-testid="stRadio"] label:not([data-testid="stWidgetLabel"]):has(input[type="radio"]:checked) {{
    background-color: #ff4b4b;
    color: white;
    border-color: #ff4b4b;
}}
"""

# CSS for a custom-styled Streamlit button
CUSTOM_BUTTON_CSS = """
{selector} [data-testid="stButton"] button {{
    background-color: #4CAF50; /* Green */
    color: white;
    border: 2px solid #4CAF50;
    border-radius: 12px;
    padding: 10px 24px;
    font-weight: bold;
    transition: all 0.3s ease;
}}
{selector} [data-testid="stButton"] button:hover {{
    background-color: white;
    color: #4CAF50;
}}
"""

class HierarchicalSidebarNavigation:
    """
    A class to manage and display hierarchical sidebar navigation in a Streamlit application,
    allowing for main sections and optional subsections, with persistent state across reruns.
    It also provides fine-grained "Previous/Next" step navigation buttons.
    """
    def __init__(self, navigation_structure, 
                 section_key_name="h_nav_main_section", 
                 last_subs_key_name="h_nav_last_active_subsections"):
        """
        Initializes the hierarchical navigation manager.

        Args:
            navigation_structure (dict): A dictionary defining the navigation hierarchy.
                Keys are main section names (str). Values are lists of subsection names (list of str)
                or None if the main section has no subsections.
                Example: {"Home": None, "Reports": ["Sales", "Marketing"]}
            section_key_name (str, optional): The key used in st.session_state to store
                the active main section. Defaults to "h_nav_main_section".
            last_subs_key_name (str, optional): The key used in st.session_state to store
                a dictionary meisjes main section names to their last active subsection.
                Defaults to "h_nav_last_active_subsections".
        """
        self.structure = navigation_structure
        self.main_sections = list(self.structure.keys())
        self.section_key = section_key_name
        self.last_subs_key = last_subs_key_name
        
        self.radio_css = self._get_sidebar_radio_css()

        if self.section_key not in st.session_state:
            st.session_state[self.section_key] = self.main_sections[0]
        if self.last_subs_key not in st.session_state:
            st.session_state[self.last_subs_key] = {}

        current_main = st.session_state[self.section_key]
        current_main_subsections = self.structure.get(current_main)
        if current_main_subsections and current_main not in st.session_state[self.last_subs_key]:
            st.session_state[self.last_subs_key][current_main] = current_main_subsections[0]

    def _get_current_active_subsection_for_main(self, main_section_name):
        """
        Retrieves the last active subsection for a given main section.

        Args:
            main_section_name (str): The name of the main section.

        Returns:
            str or None: The name of the active subsection, or None if not set or not applicable.
        """
        return st.session_state[self.last_subs_key].get(main_section_name)

    def _set_active_subsection_for_main(self, main_section_name, sub_section_name):
        """
        Sets the active subsection for a given main section.

        Args:
            main_section_name (str): The name of the main section.
            sub_section_name (str): The name of the subsection to set as active.
        """
        st.session_state[self.last_subs_key][main_section_name] = sub_section_name

    @staticmethod
    def _get_sidebar_radio_css():
        """Returns the CSS string for styling sidebar radio buttons, with escaped braces for formatting."""
        # Note the double curly braces {{ and }} to escape them for the .format() method.
        # The {selector} placeholder remains with single braces to be replaced.
        return """
            {selector} [data-testid="stRadio"] label:not([data-testid="stWidgetLabel"]) > div:first-child {{
                display: none;
            }}

            {selector} [data-testid="stRadio"] label:not([data-testid="stWidgetLabel"]) {{
                display: flex;
                align-items: center;
                justify-content: flex-start;
                
                width: 100%;
                margin-bottom: 0.5rem;
                
                background-color: transparent;
                border: 2px solid transparent;
                border-radius: 0.5rem;
                
                box-sizing: border-box;
                cursor: pointer;
                transition: all 0.2s ease-in-out;
            }}

            {selector} [data-testid="stRadio"] label:not([data-testid="stWidgetLabel"]):hover {{
                background-color: rgba(255, 75, 75, 0.1);
                border-color: rgba(255, 75, 75, 0.5);
            }}

            {selector} [data-testid="stRadio"] label:not([data-testid="stWidgetLabel"]):has(input[type="radio"]:checked) {{
                background-color: #ff4b4b;
                color: white;
                border-color: #ff4b4b;
                font-weight: 600;
            }}
        """

    def display_sidebar_navigation(self, radio_title_main="Main Section:", radio_title_sub_prefix="Subsections of"):
        """
        Displays the radio button selectors in the Streamlit sidebar for navigation.
        Updates st.session_state and triggers st.rerun() if the selection changes.

        Args:
            radio_title_main (str, optional): Title for the main section radio selector.
                                               Defaults to "Main Section:".
            radio_title_sub_prefix (str, optional): Prefix for the subsection radio selector title.
                                                     Defaults to "Subsections of".
        """
        rerun_needed = False
        current_main_section = st.session_state[self.section_key]
        current_main_section_idx = self.main_sections.index(current_main_section)

        # Usar el componente con target='sidebar'
        with StylableContainer(key="main_nav_container", css=self.radio_css, target='sidebar'):
            selected_main_section = st.radio( # st.sidebar.radio ya no es necesario, el contexto se encarga
                radio_title_main, options=self.main_sections, index=current_main_section_idx,
                key=f"{self.section_key}_radio_main")

        # ... (lógica de cambio de sección, sin cambios) ...
        if selected_main_section != current_main_section:
            st.session_state[self.section_key] = selected_main_section
            rerun_needed = True

        active_main_for_sub_selector = st.session_state[self.section_key]
        available_subsections = self.structure.get(active_main_for_sub_selector)

        if available_subsections:
            st.sidebar.markdown("---") # st.sidebar. es correcto aquí
            current_active_sub = st.session_state[self.last_subs_key].get(active_main_for_sub_selector, available_subsections[0])
            
            idx_sub = 0
            if current_active_sub in available_subsections:
                idx_sub = available_subsections.index(current_active_sub)
            
            # Aplicar estilo también a las subsecciones
            with StylableContainer(key="sub_nav_container", css=self.radio_css, target='sidebar'):
                selected_sub_section = st.radio( # Igual aquí
                    f"{radio_title_sub_prefix} '{active_main_for_sub_selector}':",
                    options=available_subsections, index=idx_sub,
                    key=f"sub_radio_{active_main_for_sub_selector.replace(' ','_')}"
                )
            
            if selected_sub_section != current_active_sub:
                self._set_active_subsection_for_main(active_main_for_sub_selector, selected_sub_section)
                rerun_needed = True
        
        elif st.session_state[self.last_subs_key].get(active_main_for_sub_selector) is not None:
             del st.session_state[self.last_subs_key][active_main_for_sub_selector]

        if rerun_needed:
            st.rerun()

    def get_active_selection(self):
        """
        Retrieves the currently active main section and subsection.

        Returns:
            tuple: (active_main_section_name, active_subsection_name or None)
        """
        active_main = st.session_state.get(self.section_key)
        active_sub = None
        if active_main and self.structure.get(active_main):
            active_sub = self._get_current_active_subsection_for_main(active_main)
        return active_main, active_sub

    def navigate_to(self, main_section_name, sub_section_name=None):
        """
        Programmatically navigates to a specified main section and, optionally, a subsection.
        Updates st.session_state and triggers st.rerun().

        Args:
            main_section_name (str): The name of the target main section.
            sub_section_name (str, optional): The name of the target subsection. If None,
                and the main section has subsections, navigates to its first (or last remembered)
                subsection. Defaults to None.
        """
        if main_section_name in self.main_sections:
            st.session_state[self.section_key] = main_section_name
            available_subs = self.structure.get(main_section_name)
            if available_subs:
                if sub_section_name and sub_section_name in available_subs:
                    self._set_active_subsection_for_main(main_section_name, sub_section_name)
                else:
                    if main_section_name not in st.session_state[self.last_subs_key] or \
                       st.session_state[self.last_subs_key][main_section_name] not in available_subs:
                        self._set_active_subsection_for_main(main_section_name, available_subs[0])
            elif main_section_name in st.session_state[self.last_subs_key]:
                 del st.session_state[self.last_subs_key][main_section_name]
            st.rerun()
        else:
            st.error(f"Navigation Error: Section '{main_section_name}' does not exist.")

    def _format_step_name(self, main_name, sub_name=None, max_len=25):
        """
        Formats the step name for display on navigation buttons, truncating if necessary.

        Args:
            main_name (str): The name of the main section.
            sub_name (str, optional): The name of the subsection. Defaults to None.
            max_len (int, optional): Maximum length for the formatted name. Defaults to 25.

        Returns:
            str: The formatted and potentially truncated step name.
        """
        if sub_name:
            full_name = f"{main_name} / {sub_name}"
        else:
            full_name = main_name
        
        if len(full_name) > max_len:
            return full_name[:max_len-3] + "..."
        return full_name

    def _get_total_steps(self):
        """Calculates the total number of navigable steps (main sections and subsections)."""
        count = 0
        for _, sub_sections_list in self.structure.items():
            if sub_sections_list:
                count += len(sub_sections_list)
            else:
                count += 1
        return count

    def _get_current_step_index(self):
        """Determines the 1-based index of the current step in the overall navigation sequence."""
        current_main, current_sub = self.get_active_selection()
        current_idx = 0
        for main_s, sub_ss_list in self.structure.items():
            if not sub_ss_list:
                current_idx += 1
                if main_s == current_main:
                    return current_idx
            else:
                for sub_s_item in sub_ss_list:
                    current_idx += 1
                    if main_s == current_main and sub_s_item == current_sub:
                        return current_idx
        return 0
    
    def create_navigation_buttons(self, 
                                  prev_text="⬅️ Previous Step",
                                  next_text="Next Step ➡️",
                                  default_prev_prefix="⬅️ ", 
                                  default_next_prefix=" ➡️", 
                                  title_home="🔼 Home",
                                  use_dynamic_names=True,
                                  show_step_count=True):
        """
        Creates Previous, Home, and Next navigation buttons.
        Button labels can be dynamic (showing a preview of the destination) or static.
        Buttons are hidden if navigation is not possible (e.g., "Previous" on the first step).

        Args:
            prev_text (str, optional): Static text for the "Previous" button
                                               if use_dynamic_names is False. Defaults to "⬅️ Previous Step".
            next_text (str, optional): Static text for the "Next" button
                                               if use_dynamic_names is False. Defaults to "Next Step ➡️".
            default_prev_prefix (str, optional): Prefix for dynamic "Previous" button label.
                                                  Defaults to "⬅️ ".
            default_next_prefix (str, optional): Suffix for dynamic "Next" button label.
                                                  Defaults to " ➡️".
            title_home (str, optional): Text for the "Home" button. Defaults to "🔼 Home".
            use_dynamic_names (bool, optional): If True, "Previous" and "Next" buttons will show
                                                a preview of the destination. Defaults to True.
            show_step_count (bool, optional): If True, displays "Step X of Y" information.
                                              Defaults to True.
        """
        current_main_section, current_sub_section = self.get_active_selection()
        
        prev_main, prev_sub = self._get_previous_step(current_main_section, current_sub_section)
        next_main, next_sub = self._get_next_step(current_main_section, current_sub_section)

        if show_step_count:
            total_steps = self._get_total_steps()
            current_step_num = self._get_current_step_index()
        
        st.markdown("---")
        col1, col_mid, col3 = st.columns([2,1,2])

        with col1:
            if prev_main is not None:
                btn_prev_text = f"{default_prev_prefix}{prev_text}"
                if use_dynamic_names:
                    if prev_text == "⬅️ Previous Step":
                        btn_prev_text = ""
                    btn_prev_text += self._format_step_name(prev_main, prev_sub)
                else:
                    btn_prev_text = prev_text
                
                if st.button(btn_prev_text, key=f"{self.section_key}_btn_prev_dyn", help=f"{prev_text}{prev_main}/{prev_sub}" if prev_sub else f"{prev_text}{prev_main}"):
                    self.navigate_to(prev_main, prev_sub)
            else:
                st.container()

        with col_mid:
            is_on_very_first_step = (prev_main is None)
            
            if not is_on_very_first_step:
                if st.button(title_home, key=f"{self.section_key}_btn_home_dyn", help='Go to the first section.'):
                    self.navigate_to(self.main_sections[0])
            elif show_step_count :
                 st.markdown(f"<div style='text-align: center; margin-top: 8px;'>Step {current_step_num} of {total_steps}</div>", unsafe_allow_html=True)
            else:
                st.container()
        
        if not is_on_very_first_step and show_step_count:
             st.caption(f"Step {current_step_num} of {total_steps}")


        with col3:
            if next_main is not None:
                btn_next_text = next_text 
                if use_dynamic_names:
                    if next_text == "Next Step ➡️":
                        btn_next_text = ""
                    btn_next_text += f"{self._format_step_name(next_main, next_sub)}{default_next_prefix}"
                
                if st.button(btn_next_text, key=f"{self.section_key}_btn_next_dyn", help=f"{prev_text}{next_main}/{next_sub}" if next_sub else next_text+next_main):
                    self.navigate_to(next_main, next_sub)
            else:
                st.container()


    def _get_next_step(self, current_main, current_sub):
        """Calculates the next step (main_section, sub_section) in the navigation sequence."""
        current_main_idx = self.main_sections.index(current_main)
        subsections_of_current_main = self.structure.get(current_main)

        if subsections_of_current_main and current_sub:
            try:
                current_sub_idx = subsections_of_current_main.index(current_sub)
                if current_sub_idx < len(subsections_of_current_main) - 1:
                    return current_main, subsections_of_current_main[current_sub_idx + 1]
            except ValueError: pass
        
        if current_main_idx < len(self.main_sections) - 1:
            next_main_section = self.main_sections[current_main_idx + 1]
            subsections_of_next_main = self.structure.get(next_main_section)
            return next_main_section, subsections_of_next_main[0] if subsections_of_next_main else None
        return None, None

    def _get_previous_step(self, current_main, current_sub):
        """Calculates the previous step (main_section, sub_section) in the navigation sequence."""
        current_main_idx = self.main_sections.index(current_main)
        subsections_of_current_main = self.structure.get(current_main)

        if subsections_of_current_main and current_sub:
            try:
                current_sub_idx = subsections_of_current_main.index(current_sub)
                if current_sub_idx > 0:
                    return current_main, subsections_of_current_main[current_sub_idx - 1]
            except ValueError: pass 
        
        if current_main_idx > 0:
            prev_main_section = self.main_sections[current_main_idx - 1]
            subsections_of_prev_main = self.structure.get(prev_main_section)
            return prev_main_section, subsections_of_prev_main[-1] if subsections_of_prev_main else None
        return None, None

# --- Example of Usage ---
if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Streamlit Extended Test")

    sample_structure = {
        "Home": None,
        "Chapter 1: Introduction": [
            "Topic 1.1: Overview",
            "Topic 1.2: Key Concepts"
        ],
        "Chapter 2: Methodology": [
            "Topic 2.1: Data Collection",
            "Topic 2.2: Analysis Techniques",
            "Topic 2.3: Limitations"
        ],
        "Chapter 3: Results": None,
        "Conclusion": None
    }
    
    navigator = HierarchicalSidebarNavigation(navigation_structure=sample_structure)

    st.sidebar.title("App Menu")
    navigator.display_sidebar_navigation(radio_title_main="Select Chapter:", radio_title_sub_prefix="Topic in")
    st.sidebar.markdown("---")
    st.sidebar.caption("This is a demo of the navigator.")

    # Get active selection
    active_main, active_sub = navigator.get_active_selection()
    # Display content based on selection
    st.header(f"Content: {active_main}")
    if active_sub:
        st.subheader(f"Sub-topic: {active_sub}")
        st.write(f"Detailed information for {active_main} -> {active_sub} would be shown here.")
        # Example of using tabs within a sub-section
        if active_main == "Chapter 2: Methodology" and active_sub == "Topic 2.2: Analysis Techniques":
            tab_data, tab_chart, tab_code = st.tabs(["Raw Data", "Visualization", "Code Snippet"])
            with tab_data:
                st.dataframe({"X": [1,2,3], "Y": [4,5,6]})
            with tab_chart:
                st.line_chart({"data": [10, 20, 5, 15]})
            with tab_code:
                st.code("print('Hello from Analysis Techniques')")
    else:
        st.write(f"General overview for {active_main}.")
        if active_main == "Home":
            st.success("Welcome to the application!")
        st.title("StylableContainer Component Example")

    st.divider()
    st.success("This version uses a clean `with` syntax and includes corrected button styling.")
    
    st.subheader("Custom Styled Radio Buttons")
#   st.markdown(f"""
#        <style>
#                
#            div[data-testid="stRadio"] label > div:first-child {{
#                display: none;
#            }}
#
#            div[data-testid="stRadio"] label {{
#                display: flex;
#                justify-content: center;
#                align-items: center;
#                
#                background-color: #262730;
#                border: 2px solid #262730;
#                border-radius: 0.75rem;
#                margin-bottom: 0.5rem;
#                width: 100%;
#                cursor: pointer;
#                transition: all 0.2s ease-in-out;
#            }}
#
#            div[data-testid="stRadio"] label:hover {{
#                background-color: #31333f;
#                border-color: #ff4b4b;
#            }}
#            
#            div[data-testid="stRadio"] label:has(input[type="radio"]:checked) {{
#                background-color: #ff4b4b;
#                color: white;
#                border-color: #ff4b4b;
#            }}
#        </style>
#        """, unsafe_allow_html=True)
    with StylableContainer(key="radio_styled_example", css=RADIO_BUTTON_CSS):
        chosen_plan = st.radio(
            "Choose your plan:", ["Basic", "Pro", "Enterprise"],
            key="plan",
            horizontal=True,
            label_visibility="collapsed"
        )
    st.write(f"You have selected the plan: **{chosen_plan}**")
    
    st.divider()

    st.subheader("Custom Styled Button")
    with StylableContainer(key="button_styled_example", css=CUSTOM_BUTTON_CSS):
        if st.button("Click the styled button!", key="btn_styled"):
            st.balloons()

    st.divider()

    st.subheader("Native Streamlit Elements (unstyled)")
    chosen_color = st.radio(
        "Choose a color:", ["Red", "Green", "Blue"], key="color"
    )
    if st.button("Normal button", key="btn_normal"):
        st.toast("Normal button pressed.")

    # Display navigation buttons
    st.markdown("---")
    navigator.create_navigation_buttons(
        prev_text="Previous: ", # Example of static text
        next_text="Next: ",
        #use_dynamic_names=True,
    )