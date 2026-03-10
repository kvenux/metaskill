"""Generate Mermaid flow diagrams, output previews, and target audience via LLM."""

import logging

from llm_client import chat_json

log = logging.getLogger(__name__)

FLOW_BATCH_SIZE = 3


def _llm_generate_batch(batch: list[dict]) -> dict:
    """Generate flow diagram + output preview + target audience for a batch of skills."""
    system_prompt = (
        "You are a skill analyst. For each skill, generate 3 things:\n\n"
        "1. flow_diagram: A Mermaid.js flowchart (graph TD) showing the skill's execution logic.\n"
        "   - Use ([text]) for entry nodes, [text] for process nodes, {text} for decisions, ((text)) for outputs\n"
        "   - Keep it 5-12 nodes. Use descriptive edge labels with |label| syntax.\n"
        "   - Example: graph TD\\n  A([User Request]) -->|Trigger| B[Analyze]\\n  B --> C{Check}\\n  C -->|Yes| D((Output))\n\n"
        "2. output_preview: A realistic example output (200-400 chars) showing what the skill produces.\n"
        "   Use markdown formatting. Show a concrete, useful example.\n\n"
        "3. target_audience: One sentence (in English) describing who benefits most from this skill.\n\n"
        'Return JSON: {"results": [{"id": "skill-id", "flow_diagram": "graph TD\\n  ...", '
        '"output_preview": "...", "target_audience": "..."}, ...]}\n'
        "If the skill content is too vague to generate a meaningful flow, set flow_diagram to empty string."
    )
    items = []
    for s in batch:
        content = (s.get("skill_md_content", "") or "")[:3000]
        items.append(
            f"ID: {s['id']}\nName: {s['name']}\n"
            f"Description: {s.get('description', '')}\n"
            f"Content:\n{content}\n---"
        )
    user_prompt = "\n".join(items)

    result = chat_json(system_prompt, user_prompt)
    if result and "results" in result:
        out = {}
        for r in result["results"]:
            sid = r.get("id", "")
            if sid:
                out[sid] = {
                    "flow_diagram": r.get("flow_diagram", ""),
                    "output_preview": r.get("output_preview", ""),
                    "target_audience": r.get("target_audience", ""),
                }
        return out
    return None


def generate_flows(skills: list[dict]) -> list[dict]:
    """Generate flow diagrams, output previews, and target audiences for all skills."""
    llm_results = {}
    for i in range(0, len(skills), FLOW_BATCH_SIZE):
        batch = skills[i : i + FLOW_BATCH_SIZE]
        results = _llm_generate_batch(batch)
        if results:
            llm_results.update(results)
            log.info("LLM generated flows for batch %d-%d", i, i + len(batch))
        else:
            log.info("LLM unavailable for flow batch %d-%d", i, i + len(batch))

    for skill in skills:
        sid = skill["id"]
        if sid in llm_results:
            data = llm_results[sid]
            skill["flow_diagram"] = data.get("flow_diagram", "")
            skill["output_preview"] = data.get("output_preview", "")
            skill["target_audience"] = data.get("target_audience", "")
        else:
            skill["flow_diagram"] = ""
            skill["output_preview"] = ""
            skill["target_audience"] = ""

    return skills
