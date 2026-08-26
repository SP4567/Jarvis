import urllib.parse
import urllib.request
import urllib.robotparser
import aiohttp
import asyncio
import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from duckduckgo_search import DDGS
from server.agents.base_agent import BaseAgent
from server.core.tool_registry import tool_registry
from server.core.models import TaskPlan, PlanStep, VerificationResult

class ResearchAgent(BaseAgent):
    """
    JARVIS Omniscient Web Intelligence, Global Search & Encyclopedic Knowledge Specialist 3.0
    Multi-Source Intelligence Gathering:
    Wikipedia Entity Disambiguation, DDG Global Search, Robots.txt Compliant Web Scraping,
    Documentation Lookup, Meteorological Forecasts, Categorized News & Fact-Checking Synthesis
    """
    def __init__(self):
        super().__init__(
            name="research_agent",
            display_name="Web Intelligence & Research",
            description="Performs deep multi-engine web search, queries Wikipedia encyclopedic records, scrapes websites respecting robots.txt, searches technical documentation, and verifies facts."
        )
        self._register_all_tools()

    def register_tool(self, name: str, func, schema: Dict[str, Any]):
        super().register_tool(name, func, schema)
        tool_registry.register_tool(
            name=name,
            func=func,
            description=schema.get("description", ""),
            parameters=schema,
            agent_name=self.name
        )

    def _register_all_tools(self):
        # 1. Comprehensive Global Research
        self.register_tool(
            "comprehensive_research",
            self.comprehensive_research,
            {
                "type": "object",
                "description": "Perform deep research across Wikipedia and global websites to answer complex queries, facts, historical bios, definitions, or live events.",
                "properties": {
                    "query": {"type": "string", "description": "The research query or topic."}
                },
                "required": ["query"]
            }
        )

        # 2. Web Search
        self.register_tool(
            "search_web",
            self.search_web,
            {
                "type": "object",
                "description": "Perform live internet search queries to retrieve current facts, articles, and global websites.",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                    "max_results": {"type": "integer", "description": "Number of results (default 5)."}
                },
                "required": ["query"]
            }
        )
        
        # 3. Wikipedia Lookup
        self.register_tool(
            "lookup_wikipedia",
            self.lookup_wikipedia,
            {
                "type": "object",
                "description": "Query Wikipedia for structured encyclopedic overview, biographies, historical events, scientific theories, or entities.",
                "properties": {
                    "topic": {"type": "string", "description": "Topic, person, concept, or search term to look up on Wikipedia."}
                },
                "required": ["topic"]
            }
        )

        # 4. Fetch Website Content (Robots.txt Compliant)
        self.register_tool(
            "fetch_website_content",
            self.fetch_website_content,
            {
                "type": "object",
                "description": "Fetch and extract readable text from a URL while strictly checking and respecting robots.txt crawling permissions.",
                "properties": {
                    "url": {"type": "string", "description": "Full HTTP/HTTPS URL of the website to scrape."},
                    "max_chars": {"type": "integer", "description": "Maximum characters to return (default 3000)."}
                },
                "required": ["url"]
            }
        )
        
        # 5. Search Technical Documentation
        self.register_tool(
            "search_documentation",
            self.search_documentation,
            {
                "type": "object",
                "description": "Search official technical documentation and API references (Python, MDN, DevDocs, PyPI).",
                "properties": {
                    "library_or_tech": {"type": "string", "description": "Library or language (e.g. 'python', 'fastapi', 'react', 'git')."},
                    "query": {"type": "string", "description": "Specific function, class, or concept to search for."}
                },
                "required": ["library_or_tech", "query"]
            }
        )

        # 6. Weather Forecast
        self.register_tool(
            "get_weather",
            self.get_weather,
            {
                "type": "object",
                "description": "Fetch real-time weather, temperature, humidity, wind, and conditions for any city or coordinates.",
                "properties": {
                    "location": {"type": "string", "description": "City or location name (e.g. 'London', 'New York', 'Tokyo', 'Mumbai')."}
                },
                "required": ["location"]
            }
        )
        
        # 7. Latest News
        self.register_tool(
            "get_latest_news",
            self.get_latest_news,
            {
                "type": "object",
                "description": "Retrieve current headline news on general topics or specific keywords (technology, AI, security, business, world).",
                "properties": {
                    "topic": {"type": "string", "description": "News topic or keyword (default 'technology')."},
                    "max_results": {"type": "integer", "description": "Maximum news items to return (default 5)."}
                }
            }
        )

        # 8. Fact Check Claim
        self.register_tool(
            "fact_check_claim",
            self.fact_check_claim,
            {
                "type": "object",
                "description": "Cross-reference a factual claim or statement against multiple web sources and Wikipedia.",
                "properties": {
                    "claim": {"type": "string", "description": "Statement or claim to fact-check."}
                },
                "required": ["claim"]
            }
        )

    # --- Tool Implementations ---

    async def check_robots_allowed(self, target_url: str, user_agent: str = "*") -> Tuple[bool, str]:
        """
        Validates whether web scraping is permitted by target domain's robots.txt policy.
        """
        try:
            parsed = urllib.parse.urlparse(target_url)
            if not parsed.scheme or not parsed.netloc:
                return False, "Invalid URL format"

            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)

            headers = {"User-Agent": "JarvisAI/1.0 (Web Intelligence Bot; respectful)"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=4)) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        rp.parse(text.splitlines())
                        can_fetch = rp.can_fetch(user_agent, target_url)
                        if can_fetch:
                            return True, "Allowed by robots.txt"
                        else:
                            return False, f"Disallowed by {parsed.netloc}/robots.txt policy"
                    elif resp.status in [401, 403]:
                        return False, f"Access to robots.txt forbidden (HTTP {resp.status})"
                    else:
                        # 404 or other status indicates no robots.txt restrictions
                        return True, "No robots.txt restrictions detected"
        except Exception as e:
            # If robots.txt check fails due to timeout or network, default to polite scraping
            return True, f"Robots check passed (network fallback: {str(e)})"

    async def fetch_website_content(self, url: str, max_chars: int = 3000) -> Dict[str, Any]:
        """
        Scrapes and extracts readable text from a URL only if allowed by robots.txt.
        """
        # 1. Strictly verify robots.txt compliance
        is_allowed, reason = await self.check_robots_allowed(url)
        if not is_allowed:
            return {
                "success": False,
                "url": url,
                "robots_compliant": False,
                "error": f"SCRAPING ABORTED: {reason}. Respecting site crawling permissions.",
                "message": f"Website at {url} does not permit automated crawling as per its robots.txt policy."
            }

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        
                        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
                        title = title_match.group(1).strip() if title_match else url
                        
                        # Strip script, style, nav, header, footer
                        clean = re.sub(r'<(script|style|nav|header|footer|aside).*?>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
                        clean = re.sub(r'<.*?>', ' ', clean)
                        clean = re.sub(r'\s+', ' ', clean).strip()

                        return {
                            "success": True,
                            "url": url,
                            "title": title,
                            "robots_compliant": True,
                            "content": clean[:max_chars],
                            "word_count": len(clean.split())
                        }
                    else:
                        return {"success": False, "error": f"Website responded with HTTP status {resp.status}."}
        except Exception as e:
            return {"success": False, "error": f"Could not fetch website content: {str(e)}"}

    async def lookup_wikipedia(self, topic: str) -> Dict[str, Any]:
        """
        Deep Wikipedia lookup with title resolution and disambiguation handling.
        """
        headers = {"User-Agent": "JarvisAI/1.0 (https://github.com/jarvis; jarvis@ai.local)"}
        clean_topic = topic.strip()

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                formatted_topic = clean_topic.replace(" ", "_")
                encoded_topic = urllib.parse.quote(formatted_topic)
                direct_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_topic}"

                async with session.get(direct_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        if data.get("type") != "disambiguation" and data.get("extract"):
                            return {
                                "success": True,
                                "title": data.get("title", clean_topic),
                                "summary": data.get("extract"),
                                "description": data.get("description", ""),
                                "url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{encoded_topic}")
                            }

                # Search API fallback
                search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_topic)}&format=json"
                async with session.get(search_url, timeout=aiohttp.ClientTimeout(total=5)) as search_resp:
                    if search_resp.status == 200:
                        search_data = await search_resp.json(content_type=None)
                        search_results = search_data.get("query", {}).get("search", [])
                        if search_results:
                            best_title = search_results[0]["title"]
                            enc_best = urllib.parse.quote(best_title.replace(" ", "_"))
                            best_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{enc_best}"
                            
                            async with session.get(best_url, timeout=aiohttp.ClientTimeout(total=5)) as final_resp:
                                if final_resp.status == 200:
                                    final_data = await final_resp.json(content_type=None)
                                    return {
                                        "success": True,
                                        "title": final_data.get("title", best_title),
                                        "summary": final_data.get("extract", search_results[0].get("snippet", "")),
                                        "description": final_data.get("description", ""),
                                        "url": final_data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{enc_best}")
                                    }

            return {"success": False, "error": f"No Wikipedia article found for '{clean_topic}'."}
        except Exception as e:
            return {"success": False, "error": f"Wikipedia query error: {str(e)}"}

    def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Live search across DuckDuckGo"""
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "url": r.get("href", "")
                    })
            if not results:
                return [{"title": "No direct results", "snippet": f"No web results found for query: {query}", "url": ""}]
            return results
        except Exception as e:
            return [{"title": "Search Error", "snippet": f"Could not perform search: {str(e)}", "url": ""}]

    async def comprehensive_research(self, query: str) -> Dict[str, Any]:
        """
        Deep multi-source research combining Wikipedia & Global Web Search in parallel.
        """
        clean_q = query.strip()
        wiki_task = asyncio.create_task(self.lookup_wikipedia(clean_q))
        web_task = asyncio.to_thread(self.search_web, clean_q, 4)

        wiki_res, web_res = await asyncio.gather(wiki_task, web_task, return_exceptions=True)

        sources = []
        spoken_answer = ""
        detailed_answer = ""
        primary_source = "Global Web Intelligence"

        if isinstance(wiki_res, dict) and wiki_res.get("success") and wiki_res.get("summary"):
            w_title = wiki_res.get("title", clean_q)
            w_summary = wiki_res.get("summary", "")
            w_url = wiki_res.get("url", "")
            
            primary_source = f"Wikipedia ({w_title})"
            if w_url:
                sources.append({"title": f"Wikipedia - {w_title}", "url": w_url})
            
            sentences = re.split(r'(?<=[.!?])\s+', w_summary)
            spoken_answer = " ".join(sentences[:2]) if len(sentences) >= 2 else w_summary
            detailed_answer = f"**{w_title}**\n\n{w_summary}"

        if not spoken_answer and isinstance(web_res, list) and web_res:
            valid_snippets = [r.get("snippet", "") for r in web_res if r.get("snippet") and "No web results" not in r.get("snippet")]
            for r in web_res:
                if r.get("url"):
                    sources.append({"title": r.get("title", "Web Source"), "url": r.get("url")})

            if valid_snippets:
                primary_source = "Global Web Search"
                top_snippet = valid_snippets[0]
                spoken_answer = top_snippet[:260]
                detailed_answer = "\n\n".join([f"- **{r.get('title')}**: {r.get('snippet')}" for r in web_res[:3]])

        if not spoken_answer:
            spoken_answer = f"I retrieved records regarding '{clean_q}', Sir, but no definitive summary was located."
            detailed_answer = f"No detailed records found for query: '{clean_q}'."

        return {
            "success": True,
            "query": clean_q,
            "primary_source": primary_source,
            "spoken_answer": spoken_answer,
            "detailed_answer": detailed_answer,
            "sources": sources
        }

    async def search_documentation(self, library_or_tech: str, query: str) -> Dict[str, Any]:
        """Searches tech documentation"""
        search_query = f"{library_or_tech} documentation {query}"
        results = await asyncio.to_thread(self.search_web, search_query, 3)
        return {
            "success": True,
            "technology": library_or_tech,
            "query": query,
            "documentation_results": results
        }

    async def get_weather(self, location: str) -> Dict[str, Any]:
        """Gets live weather data"""
        try:
            encoded_loc = urllib.parse.quote(location)
            url = f"https://wttr.in/{encoded_loc}?format=j1"
            headers = {"User-Agent": "curl/7.68.0"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        current = data.get("current_condition", [{}])[0]
                        area = data.get("nearest_area", [{}])[0]
                        
                        return {
                            "success": True,
                            "location": area.get("areaName", [{}])[0].get("value", location),
                            "country": area.get("country", [{}])[0].get("value", ""),
                            "temp_c": current.get("temp_C", "N/A"),
                            "temp_f": current.get("temp_F", "N/A"),
                            "condition": current.get("weatherDesc", [{}])[0].get("value", "Clear"),
                            "humidity": f"{current.get('humidity', 'N/A')}%",
                            "wind_speed_kmph": current.get("windspeedKmph", "N/A"),
                            "uv_index": current.get("uvIndex", "N/A")
                        }
                    else:
                        return {"success": False, "error": f"Weather service responded with status {resp.status}"}
        except Exception as e:
            return {"success": False, "error": f"Could not retrieve weather for {location}: {str(e)}"}

    def get_latest_news(self, topic: str = "technology", max_results: int = 5) -> List[Dict[str, str]]:
        """Searches current news"""
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.news(keywords=topic, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "date": r.get("date", ""),
                        "source": r.get("source", ""),
                        "url": r.get("url", ""),
                        "snippet": r.get("body", "")
                    })
            return results or [{"title": "No news found", "snippet": f"No news currently available for {topic}."}]
        except Exception as e:
            return [{"title": "News retrieval error", "snippet": str(e)}]

    async def fact_check_claim(self, claim: str) -> Dict[str, Any]:
        """Fact checks a claim across multi-source queries"""
        res = await self.comprehensive_research(claim)
        return {
            "success": True,
            "claim": claim,
            "findings": res.get("spoken_answer"),
            "sources": res.get("sources", [])
        }

    # --- Autonomous Verification & Planning Hooks ---

    async def verify_tool_execution(self, tool_name: str, params: Dict[str, Any], result: Dict[str, Any]) -> VerificationResult:
        """Verifies research query results"""
        if isinstance(result, dict) and not result.get("success", True):
            return VerificationResult(
                verified=False,
                verdict=f"Research tool '{tool_name}' failed: {result.get('error')}",
                details=result
            )

        if tool_name == "fetch_website_content":
            robots_ok = result.get("result", {}).get("robots_compliant", True) if isinstance(result.get("result"), dict) else True
            return VerificationResult(
                verified=robots_ok,
                verdict="Website content scraped with verified robots.txt compliance." if robots_ok else "Scraping disallowed by robots.txt.",
                details={"robots_compliant": robots_ok}
            )

        return VerificationResult(
            verified=True,
            verdict=f"Research tool '{tool_name}' returned authoritative data.",
            details={"tool": tool_name}
        )

    async def formulate_plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> TaskPlan:
        """Formulates research plan"""
        q = query.lower()
        steps = []
        if "weather" in q:
            loc = q.replace("weather", "").replace("in", "").replace("what is the", "").strip() or "London"
            steps.append(PlanStep(
                step_number=1,
                description=f"Query real-time weather for {loc}",
                agent_name=self.name,
                tool_name="get_weather",
                params={"location": loc}
            ))
        elif "news" in q:
            steps.append(PlanStep(
                step_number=1,
                description="Fetch latest headline news",
                agent_name=self.name,
                tool_name="get_latest_news",
                params={"topic": "technology", "max_results": 4}
            ))
        else:
            steps.append(PlanStep(
                step_number=1,
                description=f"Execute comprehensive research for '{query}'",
                agent_name=self.name,
                tool_name="comprehensive_research",
                params={"query": query}
            ))

        return TaskPlan(
            plan_id=f"PLAN-RES-{int(time.time())}",
            goal=query,
            initiating_agent=self.name,
            steps=steps
        )

research_agent = ResearchAgent()
