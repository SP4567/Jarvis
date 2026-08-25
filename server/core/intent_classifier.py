import re
import math
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel

class IntentCategory(str, Enum):
    SYSTEM_CONTROL = "system_control"
    MEDIA_PLAYER = "media_player"
    SOC_SECURITY = "soc_security"
    CODING_DEV = "coding_dev"
    PRODUCTIVITY_MEMORY = "productivity_memory"
    CONVERSATIONAL_PERSONA = "conversational_persona"
    RESEARCH_WEB = "research_web"
    WIKIPEDIA_LOOKUP = "wikipedia_lookup"
    UNKNOWN = "unknown"

class IntentResult(BaseModel):
    category: IntentCategory
    sub_action: str
    confidence: float
    slots: Dict[str, Any] = {}
    is_compound: bool = False
    sub_intents: List[Dict[str, Any]] = []
    explanation: Optional[str] = None

class HybridIntentEngine:
    """
    Advanced Enterprise Intent Classification & Slot Extraction Engine
    Combines deterministic pattern recognition, semantic keyword scoring,
    and entity slot extraction to eliminate false web-search fallbacks.
    """
    def __init__(self):
        self._init_patterns()

    def _init_patterns(self):
        # 1. SYSTEM CONTROL PATTERNS
        self.system_patterns = [
            (r"\b((?:increase|decrease|raise|lower|set|change|turn\s+(?:up|down)|adjust)\s+volume|volume\s+(?:up|down|max|mute|unmute|level)|\bset\s+volume\s+(?:to\s+)?(\d+)%?|mute|unmute)\b", "volume_control"),
            (r"\b(brightness\s+(up|down)|\bset\s+brightness\s+(to\s+)?(\d+)%?)\b", "brightness_control"),
            (r"\b(open|launch|start|run)\s+(chrome|browser|notepad|code|vscode|spotify|calc|calculator|terminal|powershell|cmd|explorer|word|excel)\b", "launch_app"),
            (r"\b(take\s+(a\s+)?screenshot|capture\s+screen|screen\s+capture)\b", "screenshot"),
            (r"\b(battery\s+level|battery\s+status|power\s+status|uptime|system\s+uptime|system\s+vitals|vitals|hardware\s+diagnostics|cpu\s+(?:usage|load))\b", "system_status"),
            (r"\b(what\s+time\s+is\s+it(?:\s+in\s+([a-zA-Z\s]+))?|current\s+time(?:\s+in\s+([a-zA-Z\s]+))?|time\s+in\s+([a-zA-Z\s]+)|time\s+zone)\b", "global_clock"),
            (r"\b(convert\s+(\d+\.?\d*)\s*([a-zA-Z]+)\s+to\s+([a-zA-Z]+))\b", "unit_conversion"),
            (r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s+(?:tip\s+)?(?:of|on)\s+(?:[\$]?\s*)?(\d+(?:\.\d+)?)", "percentage_calc"),
            (r"square\s+root\s+of\s+(\d+(?:\.\d+)?)", "sqrt_calc"),
            (r"\b(calculate|what\s+is|compute)\s+([\d\.\s\+\-\*\/\^\(\)\%sqrtpi]+)\b", "math_calculation"),
        ]

        # 2. MEDIA PLAYER PATTERNS
        self.media_patterns = [
            (r"\b(play\s+(song|music|track|video)?\s*(.*?)|start\s+playing\s+(.*?))\b", "play_media"),
            (r"\b(pause\s+music|stop\s+music|resume\s+music|next\s+track|previous\s+track|skip\s+song)\b", "media_control"),
        ]

        # 3. SOC SECURITY PATTERNS
        self.soc_patterns = [
            (r"\b(activate\s+soc|enable\s+soc|turn\s+on\s+soc|switch\s+on\s+soc|start\s+soc|enable\s+security\s+monitoring)\b", "soc_power_on"),
            (r"\b(deactivate\s+soc|disable\s+soc|turn\s+off\s+soc|switch\s+off\s+soc|stop\s+soc|standby\s+soc)\b", "soc_power_off"),
            (r"\b(tier\s*1|tier\s*one|triage\s+agent|triage\s+analyst|triage\s+alert|alert\s+triage|triage\s+queue|triage\s+report)\b", "soc_tier1_triage"),
            (r"\b(tier\s*2|tier\s*two|incident\s+responder|investigate\s+incident|investigate\s+host|attack\s+vector|blast\s+radius|incident\s+timeline)\b", "soc_tier2_investigate"),
            (r"\b(tier\s*3|tier\s*three|threat\s+hunter|threat\s+hunting|hunt\s+for\s+persistence|deobfuscate|sigma\s+rule|sigma\s+detection|yara\s+rule)\b", "soc_tier3_hunter"),
            (r"\b(mean\s+time\s+to\s+detect|mttd|mttr|soc\s+metrics|detection\s+metrics)\b", "soc_metrics"),
            (r"\b(security\s+audit|audit\s+host|audit\s+security|run\s+security\s+audit|live\s+audit|scan\s+host|scan\s+system\s+for\s+threats|endpoint\s+audit)\b", "soc_live_audit"),
            (r"\b(running\s+processes|active\s+processes|inspect\s+processes|check\s+processes|list\s+processes)\b", "soc_inspect_processes"),
            (r"\b(listening\s+ports|open\s+ports|active\s+sockets|network\s+sockets|network\s+connections)\b", "soc_inspect_sockets"),
            (r"\b(startup\s+items|startup\s+persistence|registry\s+run\s+keys|autorun|check\s+persistence)\b", "soc_inspect_persistence"),
            (r"\b(security\s+status|threat\s+posture|soc\s+status|threat\s+level|soc\s+posture|security\s+posture|soc\s+briefing|threat\s+report)\b", "soc_briefing"),
            (r"\b(isolate\s+host|isolate\s+endpoint|network\s+quarantine|block\s+ip|quarantine\s+file|kill\s+process\s+pid)\b", "soc_containment"),
            (r"\b(rollback\s+action|rollback\s+isolation|reverse\s+containment|undo\s+action)\b", "soc_rollback"),
            (r"\b(authorize\s+containment|approve\s+action|confirm\s+action)\b", "soc_authorize"),
        ]

        # 4. CODING & DEV PATTERNS
        self.coding_patterns = [
            (r"\b(write\s+(?:a\s+)?(?:python|javascript|typescript|fastapi|react|html|css|bash|sql|rust|go)?\s*(?:script|code|program|file|function)?\s*(?:for\s+)?(.*?)\s*(?:named|called|to)?\s*([a-zA-Z0-9_\-\.\/]+)?)\b", "write_code"),
            (r"\b(run|execute)\s+(?:python\s+code|python\s+script|the\s+script|file|code)[:\s]*(.*)\b", "run_code"),
            (r"\b(read|view|show|inspect)\s+(?:code|file|script)\s+([a-zA-Z0-9_\-\.\/]+)\b", "read_code"),
            (r"\b(git\s+status|git\s+branch|git\s+log|git\s+diff|git\s+commit|check\s+git\s+status)\b", "git_command"),
            (r"\b(run\s+tests|pytest|test\s+suite)\b", "run_tests"),
        ]

        # 5. PRODUCTIVITY & MEMORY PATTERNS
        self.productivity_patterns = [
            (r"\b(remember\s+(?:that\s+)?(?:my|the|our)?\s*(.*?)|store\s+(?:fact|memory|preference)\s*(.*?)|my\s+name\s+is\s+([a-zA-Z\s]+)|i\s+prefer\s+(.*?))\b", "store_fact"),
            (r"\b(what\s+is\s+my\s+(.*?)|do\s+you\s+remember\s+(.*?)|recall\s+(?:fact|memory|my)\s*(.*?)|who\s+am\s+i)\b", "recall_fact"),
            (r"\b(take\s+(?:a\s+)?note|create\s+(?:a\s+)?note|add\s+(?:a\s+)?note|save\s+note)\s*(.*)\b", "create_note"),
            (r"\b(list\s+notes|show\s+notes|my\s+notes|search\s+notes)\b", "list_notes"),
            (r"\b(set\s+(?:a\s+)?reminder|remind\s+me\s+to\s+(.*?)\s+(?:in|at|on)\s+(.*)|add\s+reminder)\b", "create_reminder"),
            (r"\b(list\s+reminders|show\s+reminders|my\s+tasks|pending\s+tasks)\b", "list_reminders"),
            (r"\b(set\s+(?:an?\s+)?alarm\s+for\s+(.*?)|wake\s+me\s+up\s+at\s+(.*?))\b", "set_alarm"),
        ]

        # 6. CONVERSATIONAL & PERSONA PATTERNS
        self.persona_patterns = [
            (r"^(hello|hi|hey|good\s+morning|good\s+afternoon|good\s+evening|greetings|jarvis|yo)\b", "greeting"),
            (r"\b(who\s+are\s+you|what\s+is\s+your\s+name|what\s+are\s+you|introduce\s+yourself)\b", "identity"),
            (r"\b(what\s+can\s+you\s+do|list\s+capabilities|your\s+skills|how\s+can\s+you\s+help)\b", "capabilities"),
            (r"\b(how\s+are\s+you|how\s+are\s+things|status\s+report|system\s+status|are\s+you\s+online)\b", "status_check"),
            (r"\b(thank\s+you|thanks|great\s+job|awesome|good\s+work|well\s+done)\b", "gratitude"),
            (r"\b(tell\s+me\s+a\s+joke|make\s+me\s+laugh|entertain\s+me|a\s+joke)\b", "joke"),
            (r"\b(motivational\s+quote|inspire\s+me|quote\s+of\s+the\s+day|quote)\b", "quote"),
            (r"\b(who\s+created\s+you|who\s+made\s+you|who\s+is\s+your\s+creator)\b", "creator"),
        ]

        # 7. WIKIPEDIA / ENCYCLOPEDIA LOOKUP PATTERNS
        self.wiki_patterns = [
            (r"\b(who\s+(?:is|was)\s+([a-zA-Z0-9\s\.\-]+))\b", "wiki_who_is"),
            (r"\b(what\s+(?:is|was)\s+(?:the\s+)?([a-zA-Z0-9\s\.\-]+))\b", "wiki_what_is"),
            (r"\b(tell\s+me\s+about\s+([a-zA-Z0-9\s\.\-]+)|explain\s+([a-zA-Z0-9\s\.\-]+)|define\s+([a-zA-Z0-9\s\.\-]+))\b", "wiki_explain"),
            (r"\b(wikipedia\s+(?:search\s+)?(?:for\s+)?([a-zA-Z0-9\s\.\-]+))\b", "wiki_direct"),
        ]

        # 8. GLOBAL WEB RESEARCH & SCRAPING PATTERNS
        self.web_patterns = [
            (r"\b(scrape|extract\s+content\s+from|fetch\s+url)\s+(https?:\/\/[^\s]+)\b", "scrape_url"),
            (r"\b(search\s+(?:the\s+)?web\s+(?:for\s+)?|google\s+|lookup\s+online\s+|search\s+online\s+for\s+)(.*)\b", "web_search"),
            (r"\b(latest\s+news\s+(?:on|about)?|current\s+events\s+(?:on|about)?|what\s+is\s+happening\s+with)\s+(.*)\b", "news_search"),
        ]

    def parse(self, text: str) -> IntentResult:
        """
        Parses text query through the Hybrid Intent Pipeline, returns structured IntentResult.
        """
        raw_text = text.strip()
        t = raw_text.lower()

        # Check for compound sentence splitters
        compound_split = re.split(r"\s+and\s+(?:also\s+|then\s+)?|\s*;\s*", raw_text, flags=re.IGNORECASE)
        if len(compound_split) > 1 and len(compound_split[0].strip()) > 3 and len(compound_split[1].strip()) > 3:
            sub_results = []
            for sub in compound_split:
                sub_clean = sub.strip()
                if sub_clean:
                    parsed_sub = self._parse_single_intent(sub_clean)
                    sub_results.append(parsed_sub.model_dump())
            
            primary = self._parse_single_intent(compound_split[0].strip())
            primary.is_compound = True
            primary.sub_intents = sub_results
            return primary

        return self._parse_single_intent(raw_text)

    def _parse_single_intent(self, text: str) -> IntentResult:
        t = text.lower().strip()

        # --- A. SYSTEM CONTROL CHECK ---
        for pat, sub_action in self.system_patterns:
            m = re.search(pat, t)
            if m:
                slots = {"match": m.group(0)}
                if sub_action == "volume_control":
                    lvl_match = re.search(r"(\d+)", t)
                    slots["level"] = int(lvl_match.group(1)) if lvl_match else None
                    slots["direction"] = "up" if "up" in t or "raise" in t or "increase" in t else "down" if "down" in t or "lower" in t or "decrease" in t else "mute" if "mute" in t else "set"
                elif sub_action == "launch_app":
                    app_m = re.search(r"\b(chrome|browser|notepad|code|vscode|spotify|calc|calculator|terminal|powershell|cmd|explorer|word|excel)\b", t)
                    slots["target_app"] = app_m.group(0) if app_m else "application"
                elif sub_action == "percentage_calc":
                    pct_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s+(?:tip\s+)?(?:of|on)\s+(?:[\$]?\s*)?(\d+(?:\.\d+)?)", t)
                    if pct_m:
                        slots["percent"] = float(pct_m.group(1))
                        slots["total"] = float(pct_m.group(2))
                elif sub_action == "sqrt_calc":
                    sq_m = re.search(r"square\s+root\s+of\s+(\d+(?:\.\d+)?)", t)
                    if sq_m:
                        slots["number"] = float(sq_m.group(1))
                elif sub_action == "unit_conversion":
                    conv_m = re.search(r"convert\s+(\d+\.?\d*)\s*([a-zA-Z]+)\s+to\s+([a-zA-Z]+)", t)
                    if conv_m:
                        slots["value"] = float(conv_m.group(1))
                        slots["from_unit"] = conv_m.group(2).lower()
                        slots["to_unit"] = conv_m.group(3).lower()
                elif sub_action == "math_calculation":
                    math_m = re.search(r"(?:calculate|what\s+is|compute)\s+([\d\.\s\+\-\*\/\^\(\)\%sqrtpi]+)", t)
                    slots["expression"] = math_m.group(1).strip() if math_m else text
                elif sub_action == "global_clock":
                    loc_m = re.search(r"(?:in\s+([a-zA-Z\s\?]+))", t)
                    slots["location"] = loc_m.group(1).strip(" ?") if loc_m else "local"
                return IntentResult(
                    category=IntentCategory.SYSTEM_CONTROL,
                    sub_action=sub_action,
                    confidence=0.98,
                    slots=slots,
                    explanation=f"System control operation: {sub_action}"
                )

        # --- B. MEDIA PLAYER CHECK ---
        if re.search(r"\b(play\s+|song\s+|music\s+|youtube\s+play|track\s+)\b", t) and not any(k in t for k in ["script", "code", "file", "role", "game"]):
            query = re.sub(r"^(jarvis\s*,?\s*)?(please\s+)?(can\s+you\s+)?(play\s+(song|music|track|video)?\s*(on\s+youtube)?\s*)", "", t).strip()
            return IntentResult(
                category=IntentCategory.MEDIA_PLAYER,
                sub_action="play_media",
                confidence=0.95,
                slots={"query": query or "ambient cyber music"},
                explanation="Media playback request"
            )

        # --- C. SOC SECURITY CHECK ---
        for pat, sub_action in self.soc_patterns:
            m = re.search(pat, t)
            if m:
                slots = {"match": m.group(0)}
                if "pid" in t:
                    pid_m = re.search(r"pid\s*(\d+)", t)
                    if pid_m:
                        slots["pid"] = int(pid_m.group(1))
                if "ip" in t:
                    ip_m = re.search(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b", t)
                    if ip_m:
                        slots["ip"] = ip_m.group(1)
                return IntentResult(
                    category=IntentCategory.SOC_SECURITY,
                    sub_action=sub_action,
                    confidence=0.99,
                    slots=slots,
                    explanation=f"Cyber SOC security command: {sub_action}"
                )

        # --- D. CODING & DEV CHECK ---
        for pat, sub_action in self.coding_patterns:
            m = re.search(pat, t)
            if m:
                slots = {"match": m.group(0)}
                if sub_action == "run_code":
                    code_m = re.search(r"(?:run|execute)\s+(?:python\s+code|python\s+script|the\s+script|file|code)[:\s]*(.*)", t)
                    slots["code"] = code_m.group(1).strip() if code_m else text
                file_m = re.search(r"([a-zA-Z0-9_\-]+\.(?:py|js|ts|html|css|json|txt|md|sh))", t)
                if file_m:
                    slots["filename"] = file_m.group(1)
                lang_m = re.search(r"\b(python|javascript|typescript|fastapi|react|html|css|bash|sql|rust|go)\b", t)
                if lang_m:
                    slots["language"] = lang_m.group(1)
                return IntentResult(
                    category=IntentCategory.CODING_DEV,
                    sub_action=sub_action,
                    confidence=0.96,
                    slots=slots,
                    explanation=f"Software engineering request: {sub_action}"
                )

        # --- E. PRODUCTIVITY & MEMORY CHECK ---
        for pat, sub_action in self.productivity_patterns:
            m = re.search(pat, t)
            if m:
                slots = {"match": m.group(0)}
                if sub_action == "store_fact":
                    fact_m = re.search(r"(?:remember\s+(?:that\s+)?|store\s+(?:fact\s+)?)(.*)", t)
                    fact_str = fact_m.group(1).strip() if fact_m else t
                    slots["fact"] = fact_str
                elif sub_action == "recall_fact":
                    query_m = re.search(r"(?:what\s+is\s+my\s+|do\s+you\s+remember\s+|recall\s+)(.*)", t)
                    slots["query"] = query_m.group(1).strip() if query_m else t
                elif sub_action == "create_note":
                    note_m = re.search(r"(?:note\s*:?\s*)(.*)", t)
                    slots["content"] = note_m.group(1).strip() if note_m else t
                return IntentResult(
                    category=IntentCategory.PRODUCTIVITY_MEMORY,
                    sub_action=sub_action,
                    confidence=0.95,
                    slots=slots,
                    explanation=f"Productivity & Memory operation: {sub_action}"
                )

        # --- F. CONVERSATIONAL & PERSONA CHECK ---
        for pat, sub_action in self.persona_patterns:
            m = re.search(pat, t)
            if m:
                return IntentResult(
                    category=IntentCategory.CONVERSATIONAL_PERSONA,
                    sub_action=sub_action,
                    confidence=0.94,
                    slots={"text": text},
                    explanation=f"JARVIS persona interaction: {sub_action}"
                )

        # --- G. WEB SCRAPING & URL FETCH ---
        if re.search(r"https?:\/\/[^\s]+", text):
            url_m = re.search(r"https?:\/\/[^\s]+", text)
            return IntentResult(
                category=IntentCategory.RESEARCH_WEB,
                sub_action="scrape_url",
                confidence=0.99,
                slots={"url": url_m.group(0)},
                explanation="Direct URL scraping request"
            )

        # --- H. EXPLICIT WEB SEARCH ---
        for pat, sub_action in self.web_patterns:
            m = re.search(pat, t)
            if m:
                query = re.sub(r"^(search\s+(?:the\s+)?web\s+(?:for\s+)?|google\s+|lookup\s+online\s+|search\s+online\s+for\s+)", "", t).strip()
                return IntentResult(
                    category=IntentCategory.RESEARCH_WEB,
                    sub_action=sub_action,
                    confidence=0.92,
                    slots={"query": query or text},
                    explanation="Explicit global web research"
                )

        # --- I. WIKIPEDIA LOOKUP ---
        for pat, sub_action in self.wiki_patterns:
            m = re.search(pat, t)
            if m:
                entity = text
                for p in ["who is", "who was", "what is", "what was", "tell me about", "explain", "define", "wikipedia search for", "wikipedia"]:
                    if entity.lower().startswith(p):
                        entity = entity[len(p):].strip()
                entity = re.sub(r"^(the|a|an)\s+", "", entity, flags=re.IGNORECASE).strip(" ?.")
                return IntentResult(
                    category=IntentCategory.WIKIPEDIA_LOOKUP,
                    sub_action=sub_action,
                    confidence=0.90,
                    slots={"entity": entity or text},
                    explanation=f"Wikipedia knowledge lookup for: {entity}"
                )

        # Default to Conversational Persona rather than forcing an empty web search
        return IntentResult(
            category=IntentCategory.CONVERSATIONAL_PERSONA,
            sub_action="general_dialogue",
            confidence=0.70,
            slots={"text": text},
            explanation="General conversational query"
        )

intent_engine = HybridIntentEngine()
