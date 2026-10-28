"""
GrammarlyX — Intelligent Grammar & Style Checker using LLM
Streamlit Production Application

Core Concept: Explain + Improve + Adapt to Context
"""

import os
import streamlit as st
import config
from utils import (
    validate_input_text,
    sanitize_input_text,
    calculate_quality_scores,
    generate_text_report,
    generate_highlighted_html,
)
from services import (
    analyze_text,
    OpenAIService,
    OpenAIServiceError,
    GrammarCheckerService,
    StyleCheckerService,
    EducationCheckerService,
)

# -----------------------------------------------------------------------------
# Page Configuration & Professional Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="GrammarlyX — Intelligent Grammar & Style Checker",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for SaaS aesthetics
st.markdown(
    """
    <style>
    /* Global typography and container adjustments */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }
    
    /* Header styling */
    .app-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    .app-subtitle {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .badge-pill {
        display: inline-block;
        background-color: #e0e7ff;
        color: #3730a3;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-right: 6px;
        margin-bottom: 8px;
    }
    
    /* Metric Card Styling */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
    }
    .metric-label {
        font-size: 0.82rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* Issue Cards */
    .issue-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .style-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 14px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .edu-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #2563eb;
        border-radius: 8px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    /* Tag labels */
    .tag-error {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .tag-warning {
        background-color: #fef3c7;
        color: #92400e;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .tag-category {
        background-color: #f1f5f9;
        color: #334155;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Initialize Session State
# -----------------------------------------------------------------------------
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if "input_text" not in st.session_state:
    st.session_state.input_text = ""


# API configuration is loaded from config.py / Streamlit Secrets.
# Do not store or display the secret in the sidebar.
if "session_api_key" in st.session_state:
    del st.session_state["session_api_key"]

if "session_provider" not in st.session_state:
    st.session_state.session_provider = "Groq (Free Tier)"

if "session_base_url" not in st.session_state:
    st.session_state.session_base_url = config.OPENAI_BASE_URL or ""

if "session_model" not in st.session_state:
    st.session_state.session_model = config.OPENAI_MODEL

# -----------------------------------------------------------------------------
# Sidebar: Controls & Settings
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### **GrammarlyX**")
    st.caption("AI-Powered Writing Quality Engine")
    st.markdown("---")

    if config.is_api_configured():
        st.success(f"🔒 API configured: {config.get_configured_model()}")
    else:
        st.error("API key missing. Configure it in Streamlit Cloud Secrets.")

    st.markdown("---")

    # 1. Writing Context
    st.markdown("#### **Writing Context**")
    selected_context = st.selectbox(
        "Target Writing Context",
        options=config.WRITING_CONTEXTS,
        index=0,
        help="GrammarlyX adapts corrections and stylistic guidance to the domain context.",
        label_visibility="collapsed",
    )
    context_hint = config.CONTEXT_GUIDELINES.get(selected_context, "")
    st.caption(f"_{context_hint}_")

    # 2. Writing Tone
    st.markdown("#### **Writing Tone**")
    selected_tone = st.selectbox(
        "Target Writing Tone",
        options=config.WRITING_TONES,
        index=0,
        help="Target emotional and structural register.",
        label_visibility="collapsed",
    )
    tone_hint = config.TONE_GUIDELINES.get(selected_tone, "")
    st.caption(f"_{tone_hint}_")

    st.markdown("---")

    # 3. Analysis Options
    st.markdown("#### **Analysis Options**")
    check_grammar = st.checkbox("Grammar & Mechanics", value=True)
    check_style = st.checkbox("Style & Conciseness", value=True)
    check_stats = st.checkbox("Writing Statistics", value=True)

    # 4. Education Mode Toggle
    st.markdown("---")
    st.markdown("#### **Education Mode**")
    # Default to True when Education or Academic Research is chosen
    auto_edu = selected_context in ["Education", "Academic Research"]
    learning_mode = st.toggle(
        "Enable Learning Mode",
        value=auto_edu,
        help="Provides in-depth pedagogical breakdowns, underlying grammatical rules, and mnemonics.",
    )
    if learning_mode:
        st.caption("Active: Educational explanations and memory tips will be generated.")

    st.markdown("---")

    # Convenience Demo Text Selector
    st.markdown("#### **Load Sample Text**")
    demo_choice = st.selectbox(
        "Choose an example:",
        options=["(Select a sample text)"] + list(config.DEMO_TEXTS.keys()),
        index=0,
    )
    if demo_choice != "(Select a sample text)":
        if st.button("Load Sample Text", use_container_width=True):
            st.session_state.input_text = config.DEMO_TEXTS[demo_choice]
            st.session_state.analysis_results = None
            st.rerun()

# -----------------------------------------------------------------------------
# Main Header Area
# -----------------------------------------------------------------------------
st.markdown('<div class="app-title">GrammarlyX</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Intelligent Grammar & Style Checker powered by GPT — <em>Explain + Improve + Adapt to Context</em></div>',
    unsafe_allow_html=True,
)

# Context and Tone status badges
st.markdown(
    f"""
    <div>
        <span class="badge-pill">Context: {selected_context}</span>
        <span class="badge-pill">Tone: {selected_tone}</span>
        <span class="badge-pill">Learning Mode: {'ON' if learning_mode else 'OFF'}</span>
        <span class="badge-pill">Model: {config.get_configured_model()}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Main Input Area
# -----------------------------------------------------------------------------
text_input = st.text_area(
    "Enter or paste your text",
    value=st.session_state.input_text,
    height=200,
    placeholder="Enter or paste your writing here for deep grammatical, stylistic, and educational analysis...",
    key="main_text_area",
)

# Update session state text
st.session_state.input_text = text_input

# Word and Character live counter
current_words = len(text_input.strip().split()) if text_input.strip() else 0
current_chars = len(text_input)
col_count1, col_count2, _ = st.columns([2, 2, 6])
with col_count1:
    st.caption(f"**Word Count:** {current_words}")
with col_count2:
    st.caption(f"**Characters:** {current_chars} / {config.MAX_INPUT_CHARS}")

# Action Buttons
btn_col1, btn_col2, _ = st.columns([2, 1.5, 6])
with btn_col1:
    analyze_clicked = st.button("🔍 Analyze Text", type="primary", use_container_width=True)
with btn_col2:
    clear_clicked = st.button("🗑️ Clear", use_container_width=True)

if clear_clicked:
    st.session_state.input_text = ""
    st.session_state.analysis_results = None
    st.rerun()

# -----------------------------------------------------------------------------
# Analysis Execution Logic
# -----------------------------------------------------------------------------
if analyze_clicked:
    # 1. Input Validation
    is_valid, error_msg = validate_input_text(text_input)
    if not is_valid:
        st.warning(error_msg)
    else:
        # 2. Check OpenAI API availability
        current_api_key =config.OPENAI_API_KEY
        if not current_api_key or current_api_key.startswith("your_") or len(current_api_key) < 10:
            st.error(
                "OpenAI API configuration is missing. "
                "Please add OPENAI_API_KEY to your .env file or enter your API key in the sidebar."
            )
        else:
            sanitized = sanitize_input_text(text_input)

            # Execution with progress feedback
            with st.spinner("Analyzing grammar, style, and structure with GPT..."):
                try:
                    openai_service = OpenAIService(
                        api_key=current_api_key,
                        model=config.OPENAI_MODEL,
                        base_url=config.OPENAI_BASE_URL,
)

                    # Deterministic text statistics
                    stats = analyze_text(sanitized) if check_stats else {}

                    # Grammar Check
                    grammar_result = {"corrected_text": sanitized, "errors": []}
                    if check_grammar:
                        grammar_checker = GrammarCheckerService(openai_service)
                        grammar_result = grammar_checker.check_grammar(
                            text=sanitized,
                            context=selected_context,
                            tone=selected_tone,
                        )

                    # Style Check
                    style_result = {"style_issues": []}
                    if check_style:
                        style_checker = StyleCheckerService(openai_service)
                        style_result = style_checker.check_style(
                            text=sanitized,
                            context=selected_context,
                            tone=selected_tone,
                        )

                    # Education Mode
                    education_result = {"lessons": []}
                    if learning_mode:
                        edu_checker = EducationCheckerService(openai_service)
                        education_result = edu_checker.check_education(
                            text=sanitized,
                            context=selected_context,
                        )

                    # Deterministic Quality Scoring
                    errors_list = grammar_result.get("errors") if check_grammar else None
                    styles_list = style_result.get("style_issues") if check_style else None
                    reading_ease = stats.get("flesch_reading_ease") if check_stats else None

                    scores = calculate_quality_scores(
                        word_count=stats.get("word_count", current_words),
                        errors=errors_list,
                        style_issues=styles_list,
                        flesch_reading_ease=reading_ease,
                    )

                    # Store results in session state
                    st.session_state.analysis_results = {
                        "original_text": sanitized,
                        "corrected_text": grammar_result.get("corrected_text", sanitized),
                        "errors": grammar_result.get("errors", []),
                        "style_issues": style_result.get("style_issues", []),
                        "detected_tone": style_result.get("detected_tone", "Neutral"),
                        "formality_score": style_result.get("formality_score", 50),
                        "formality_level": style_result.get("formality_level", "Neutral"),
                        "tone_verdict": style_result.get("tone_verdict", "Acceptable"),
                        "tone_feedback": style_result.get("tone_feedback", ""),
                        "lessons": education_result.get("lessons", []),
                        "stats": stats,
                        "scores": scores,
                        "context": selected_context,
                        "tone": selected_tone,
                        "learning_mode": learning_mode,
                        "model": config.get_configured_model(),
                    }

                except OpenAIServiceError as e:
                    st.error(f"**Analysis Error:** {e.message}")
                except Exception as e:
                    st.error(f"An unexpected error occurred during analysis: {str(e)}")

# -----------------------------------------------------------------------------
# Results Presentation
# -----------------------------------------------------------------------------
results = st.session_state.analysis_results

if results:
    st.markdown("---")
    st.markdown("### **Analysis Results**")

    scores = results["scores"]
    stats = results["stats"]
    errors = results["errors"]
    style_issues = results["style_issues"]
    lessons = results["lessons"]
    corrected_text = results["corrected_text"]
    original_text = results["original_text"]

    # 1. Overall AI Writing Quality Indicator Cards
    score_col1, score_col2, score_col3, score_col4 = st.columns(4)

    with score_col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value" style="color: {'#16a34a' if scores.overall_score >= 80 else '#d97706' if scores.overall_score >= 60 else '#dc2626'};">
                    {scores.overall_score}<span style="font-size: 1.1rem; color: #64748b;">/100</span>
                </div>
                <div class="metric-label">AI Writing Quality Indicator</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with score_col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{scores.grammar_score}<span style="font-size: 1.1rem; color: #64748b;">/100</span></div>
                <div class="metric-label">Grammar Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with score_col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{scores.style_score}<span style="font-size: 1.1rem; color: #64748b;">/100</span></div>
                <div class="metric-label">Style & Tone Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with score_col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{scores.readability_score}<span style="font-size: 1.1rem; color: #64748b;">/100</span></div>
                <div class="metric-label">Readability Score</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(f"**Rating Descriptor:** {scores.rating_label} | _{scores.formula_summary}_")

    # 2. Structured Tabs
    tab_titles = [
        "✨ Corrected Text",
        f"🔴 Grammar Issues ({len(errors)})",
        f"🟡 Style Suggestions ({len(style_issues)})",
    ]
    if results["learning_mode"]:
        tab_titles.append(f"🎓 Education ({len(lessons)})")
    tab_titles.append("📊 Statistics")

    tabs = st.tabs(tab_titles)

    # TAB 1: Corrected Text
    with tabs[0]:
        st.markdown("#### **Improved & Polished Text**")
        st.caption("Copy-friendly corrected text reflecting grammatical corrections and context requirements.")

        st.text_area(
            "Copyable Corrected Output",
            value=corrected_text,
            height=180,
            label_visibility="collapsed",
        )

        # Highlighted view of original text
        if errors or style_issues:
            st.markdown("#### **Interactive Issue Highlighting in Original Text**")
            st.caption(
                "Hover over highlighted phrases to view category and suggestion. "
                "🔴 Red indicates grammar/spelling errors; 🟡 Amber indicates style/tone suggestions."
            )
            highlighted_html = generate_highlighted_html(original_text, errors, style_issues)
            st.markdown(highlighted_html, unsafe_allow_html=True)

        # Side-by-side comparison
        with st.expander("Compare Original vs. Corrected Side-by-Side"):
            cmp_col1, cmp_col2 = st.columns(2)
            with cmp_col1:
                st.markdown("**Original Text:**")
                st.info(original_text)
            with cmp_col2:
                st.markdown("**Corrected Text:**")
                st.success(corrected_text)

    # TAB 2: Grammar Issues
    with tabs[1]:
        st.markdown(f"#### **Grammar & Mechanical Issues ({len(errors)})**")
        if not errors:
            st.success("🎉 No grammar, spelling, or punctuation errors were detected in your text!")
        else:
            for idx, err in enumerate(errors, start=1):
                sev = err.get("severity", "error").lower()
                tag_class = "tag-error" if sev == "error" else "tag-warning"
                badge_text = "Error" if sev == "error" else "Warning"

                st.markdown(
                    f"""
                    <div class="issue-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div>
                                <span class="{tag_class}">{badge_text}</span>
                                <span class="tag-category" style="margin-left: 6px;">{err.get('type', 'Grammar')}</span>
                            </div>
                            <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 600;">#{idx}</span>
                        </div>
                        <div style="margin: 8px 0; font-size: 1rem;">
                            <span style="text-decoration: line-through; color: #dc2626; font-weight: 600;">{err.get('original', '')}</span>
                            &nbsp;➔&nbsp;
                            <span style="color: #16a34a; font-weight: 700; background-color: #f0fdf4; padding: 2px 6px; border-radius: 4px;">{err.get('correction', '')}</span>
                        </div>
                        <div style="color: #334155; font-size: 0.92rem; margin-top: 6px;">
                            <strong>Why:</strong> {err.get('explanation', '')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if err.get("learning_tip"):
                    st.caption(f"💡 **Learning Tip:** {err.get('learning_tip')}")

    # TAB 3: Style Suggestions
    with tabs[2]:
        st.markdown(f"#### **Tone & Formality Assessment**")

        detected_tone = results.get("detected_tone", "Neutral")
        target_tone = results.get("tone", "Neutral")
        formality_lvl = results.get("formality_level", "Neutral")
        formality_score = results.get("formality_score", 50)
        tone_verdict = results.get("tone_verdict", "Acceptable")
        tone_feedback = results.get("tone_feedback", "")

        t_col1, t_col2, t_col3 = st.columns(3)
        with t_col1:
            st.metric(
                label="Detected Tone",
                value=detected_tone,
                help=f"Target Tone: {target_tone}",
            )
        with t_col2:
            st.metric(
                label="Formality Level",
                value=formality_lvl,
                delta=f"{formality_score}/100 Formality Score",
            )
        with t_col3:
            st.metric(
                label="Tone Alignment",
                value=tone_verdict,
            )

        if tone_feedback:
            if "mismatch" in tone_verdict.lower() or "adjustment" in tone_verdict.lower() or "informal" in formality_lvl.lower() and target_tone in ["Formal", "Academic"]:
                st.warning(f"**Tone & Style Evaluation:** {tone_feedback}")
            else:
                st.info(f"**Tone & Style Evaluation:** {tone_feedback}")

        st.markdown(f"#### **Style & Conciseness Suggestions ({len(style_issues)})**")
        if not style_issues:
            st.success(f"✨ Excellent style! The text aligns cleanly with the '{results['context']}' context.")
        else:
            for idx, issue in enumerate(style_issues, start=1):
                st.markdown(
                    f"""
                    <div class="style-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div>
                                <span class="tag-warning">Suggestion</span>
                                <span class="tag-category" style="margin-left: 6px;">{issue.get('category', 'Style')}</span>
                            </div>
                            <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 600;">#{idx}</span>
                        </div>
                        <div style="margin: 8px 0; font-size: 0.95rem;">
                            <span style="color: #9a3412; font-style: italic;">"{issue.get('text', '')}"</span>
                            &nbsp;➔&nbsp;
                            <span style="color: #0284c7; font-weight: 600;">{issue.get('suggestion', '')}</span>
                        </div>
                        <div style="color: #334155; font-size: 0.92rem; margin-top: 6px;">
                            <strong>Rationale:</strong> {issue.get('explanation', '')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # TAB 4: Education (if enabled)
    current_tab_idx = 3
    if results["learning_mode"]:
        with tabs[current_tab_idx]:
            st.markdown(f"#### **Education Mode — Pedagogical Lesson Breakdown ({len(lessons)})**")
            st.caption(
                "GrammarlyX goes beyond raw corrections to teach the foundational English grammar and stylistic principles."
            )

            if not lessons:
                st.info("No educational lessons were needed because no grammatical mistakes were found!")
            else:
                for idx, lesson in enumerate(lessons, start=1):
                    st.markdown(
                        f"""
                        <div class="edu-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <div>
                                    <span style="background-color: #dbeafe; color: #1e40af; padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 0.8rem;">
                                        {lesson.get('category', 'Grammar Concept')}
                                    </span>
                                </div>
                                <span style="color: #94a3b8; font-size: 0.85rem; font-weight: 600;">Lesson #{idx}</span>
                            </div>
                            <div style="margin: 10px 0; font-size: 1.05rem;">
                                <span style="text-decoration: line-through; color: #ef4444; font-weight: 600;">{lesson.get('mistake', '')}</span>
                                &nbsp;➔&nbsp;
                                <span style="color: #15803d; font-weight: 700;">{lesson.get('correction', '')}</span>
                            </div>
                            <div style="margin-top: 8px; font-size: 0.92rem; color: #1e293b;">
                                <strong>Core Grammatical Rule:</strong> {lesson.get('rule', '')}
                            </div>
                            <div style="margin-top: 6px; font-size: 0.92rem; color: #334155;">
                                <strong>Why this was wrong:</strong> {lesson.get('why_wrong', '')}
                            </div>
                            <div style="margin-top: 6px; font-size: 0.92rem; color: #0369a1; background-color: #f0f9ff; padding: 8px 12px; border-radius: 6px;">
                                <strong>🧠 How to Remember:</strong> {lesson.get('how_to_remember', '')}
                            </div>
                            <div style="margin-top: 8px; font-size: 0.88rem; color: #475569;">
                                <em>Model Example:</em> <code>{lesson.get('correct_example', '')}</code>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        current_tab_idx += 1

    # TAB 5: Statistics
    with tabs[current_tab_idx]:
        st.markdown("#### **Deterministic Text Statistics**")
        st.caption("Calculated in pure Python without calling LLM endpoints.")

        stat_row1_col1, stat_row1_col2, stat_row1_col3, stat_row1_col4 = st.columns(4)
        with stat_row1_col1:
            st.metric("Total Words", stats.get("word_count", 0))
        with stat_row1_col2:
            st.metric("Total Characters", stats.get("char_count", 0))
        with stat_row1_col3:
            st.metric("Sentences", stats.get("sentence_count", 0))
        with stat_row1_col4:
            st.metric("Paragraphs", stats.get("paragraph_count", 0))

        stat_row2_col1, stat_row2_col2, stat_row2_col3, stat_row2_col4 = st.columns(4)
        with stat_row2_col1:
            st.metric("Avg Words / Sentence", f"{stats.get('avg_words_per_sentence', 0):.1f}")
        with stat_row2_col2:
            st.metric("Avg Word Length", f"{stats.get('avg_word_length', 0):.1f} chars")
        with stat_row2_col3:
            st.metric("Flesch Reading Ease", f"{stats.get('flesch_reading_ease', 0):.1f}")
        with stat_row2_col4:
            st.metric("Est. Reading Time", f"{stats.get('estimated_reading_time_mins', 0):.1f} min")

        st.info(
            f"**Readability Assessment:** {stats.get('readability_grade', 'N/A')} "
            f"(Flesch-Kincaid Grade Level: {stats.get('flesch_kincaid_grade', 0.0):.1f})"
        )

        if stats.get("longest_sentence_text"):
            with st.expander("View Longest Sentence"):
                st.write(
                    f"**Length:** {stats.get('longest_sentence_words', 0)} words\n\n"
                    f"_{stats.get('longest_sentence_text')}_"
                )

    # 3. Download Feature
    st.markdown("---")
    st.markdown("#### **Download Analysis Report**")
    st.caption("Generate and export a comprehensive `.txt` report containing all scores, corrections, and metrics.")

    tone_info_payload = {
        "detected_tone": results.get("detected_tone", "Neutral"),
        "formality_score": results.get("formality_score", 50),
        "formality_level": results.get("formality_level", "Neutral"),
        "tone_verdict": results.get("tone_verdict", "Acceptable"),
        "tone_feedback": results.get("tone_feedback", ""),
    }

    try:
        report_text = generate_text_report(
            original_text=original_text,
            corrected_text=corrected_text,
            context=results["context"],
            tone=results["tone"],
            learning_mode=results["learning_mode"],
            model_name=results["model"],
            scores=scores,
            stats=stats,
            grammar_errors=errors,
            style_issues=style_issues,
            educational_lessons=lessons,
            tone_info=tone_info_payload,
        )
    except TypeError:
        report_text = generate_text_report(
            original_text=original_text,
            corrected_text=corrected_text,
            context=results["context"],
            tone=results["tone"],
            learning_mode=results["learning_mode"],
            model_name=results["model"],
            scores=scores,
            stats=stats,
            grammar_errors=errors,
            style_issues=style_issues,
            educational_lessons=lessons,
        )

    st.download_button(
        label="📥 Download Analysis Report (.txt)",
        data=report_text,
        file_name="grammarlyx_analysis_report.txt",
        mime="text/plain",
        type="secondary",
    )
