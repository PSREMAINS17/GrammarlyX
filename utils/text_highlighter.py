"""
Safe HTML highlighting utility for GrammarlyX.
Highlights grammar errors and style warnings in the original text
with tooltip explanations while strictly protecting against HTML injection.
"""

import html
import re
from typing import List, Dict, Any


def generate_highlighted_html(
    text: str,
    grammar_errors: List[Dict[str, Any]] = None,
    style_issues: List[Dict[str, Any]] = None,
) -> str:
    """
    Produce safe, CSS-styled HTML with highlighted words/phrases for detected issues.
    Falls back gracefully to escaped text if an error occurs.
    """
    if not text:
        return ""

    grammar_errors = grammar_errors or []
    style_issues = style_issues or []

    try:
        # Collect replacement spans with (start, end, style_class, tooltip, label)
        spans = []

        # Find occurrences for grammar errors (red highlight)
        for err in grammar_errors:
            orig = err.get("original", "").strip()
            if not orig:
                continue
            # Escape regex special characters
            pattern = re.escape(orig)
            for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                spans.append({
                    "start": m.start(),
                    "end": m.end(),
                    "type": "grammar",
                    "correction": err.get("correction", ""),
                    "reason": err.get("explanation", ""),
                    "category": err.get("type", "Grammar Error"),
                })

        # Find occurrences for style issues (amber highlight)
        for issue in style_issues:
            snippet = issue.get("text", "").strip()
            if not snippet:
                continue
            pattern = re.escape(snippet)
            for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                spans.append({
                    "start": m.start(),
                    "end": m.end(),
                    "type": "style",
                    "correction": issue.get("suggestion", ""),
                    "reason": issue.get("explanation", ""),
                    "category": issue.get("category", "Style Suggestion"),
                })

        # Sort spans by start index, filtering overlapping spans
        spans.sort(key=lambda s: (s["start"], -(s["end"] - s["start"])))

        non_overlapping = []
        last_end = 0
        for span in spans:
            if span["start"] >= last_end:
                non_overlapping.append(span)
                last_end = span["end"]

        # Build highlighted HTML
        html_chunks = []
        cursor = 0

        for span in non_overlapping:
            # Append plain text before this span
            if span["start"] > cursor:
                plain_segment = text[cursor:span["start"]]
                html_chunks.append(html.escape(plain_segment))

            # Segment to highlight
            target_segment = text[span["start"]:span["end"]]
            escaped_target = html.escape(target_segment)
            category_esc = html.escape(span["category"])
            reason_esc = html.escape(span["reason"][:120])
            correction_esc = html.escape(span["correction"])

            tooltip = f"[{category_esc}] {reason_esc}"
            if correction_esc:
                tooltip += f" -> Suggestion: {correction_esc}"

            if span["type"] == "grammar":
                styled = (
                    f'<span title="{tooltip}" style="background-color: #fee2e2; '
                    f'border-bottom: 2px solid #ef4444; color: #991b1b; padding: 2px 5px; '
                    f'border-radius: 4px; font-weight: 500; cursor: help;">'
                    f'{escaped_target}'
                    f'</span>'
                )
            else:
                styled = (
                    f'<span title="{tooltip}" style="background-color: #fef3c7; '
                    f'border-bottom: 2px solid #f59e0b; color: #92400e; padding: 2px 5px; '
                    f'border-radius: 4px; font-weight: 500; cursor: help;">'
                    f'{escaped_target}'
                    f'</span>'
                )

            html_chunks.append(styled)
            cursor = span["end"]

        # Append remaining text
        if cursor < len(text):
            html_chunks.append(html.escape(text[cursor:]))

        final_content = "".join(html_chunks).replace("\n", "<br>")

        container = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    font-size: 15px; line-height: 1.7; padding: 18px 20px; background-color: #f8fafc;
                    border: 1px solid #e2e8f0; border-radius: 8px; color: #1e293b; white-space: pre-wrap; word-break: break-word;">
            {final_content}
        </div>
        """
        return container

    except Exception:
        # Failsafe fallback
        escaped = html.escape(text).replace("\n", "<br>")
        return f"<div style='padding: 12px; font-family: sans-serif;'>{escaped}</div>"
