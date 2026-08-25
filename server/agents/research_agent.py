import urllib.parse
import urllib.request
import aiohttp
import asyncio
import json
import re
from typing import Dict, Any, List, Optional
from duckduckgo_search import DDGS
from server.agents.base_agent import BaseAgent
from server.core.tool_registry import tool_registry

class ResearchAgent(BaseAgent):
    """
    JARVIS Omniscient Web Intelligence, Global Search & Encyclopedic Knowledge Specialist
    """
    def __init__(self):
        super().__init__(
            name="research_agent",
            display_name="Web Intelligence & Research",
            description="Performs deep multi-engine web search, queries Wikipedia encyclopedic records, scrapes global websites, and fetches breaking news & meteorology."
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
                "name": "comprehensive_research",
                "description": "Perform deep research across Wikipedia and global websites to answer complex queries, facts, historical bios, definitions, or live events.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The research query or topic."}
                    },
                    "required": ["query"]
                }
            }
        )

        # 2. Web Search
        self.register_tool(
            "search_web",
            self.search_web,
            {
                "name": "search_web",
                "description": "Perform live internet search queries to retrieve current facts, articles, and global websites.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query."}
                    },
                    "required": ["query"]
                }
            }
        )
        
        # 3. Wikipedia Lookup
        self.register_tool(
            "lookup_wikipedia",
            self.lookup_wikipedia,
            {
                "name": "lookup_wikipedia",
                "description": "Query Wikipedia for structured encyclopedic overview, biographies, historical events, scientific theories, or entities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic, person, concept, or search term to look up on Wikipedia."}
                    },
                    "required": ["topic"]
                }
            }
        )

        # 4. Fetch Website Content
        self.register_tool(
            "fetch_website_content",
            self.fetch_website_content,
            {
                "name": "fetch_website_content",
                "description": "Fetch and extract clean readable text from any specific global URL.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Full HTTP/HTTPS URL of the website to scrape."}
                    },
                    "required": ["url"]
                }
            }
        )
        
        # 5. Weather
        self.register_tool(
            "get_weather",
            self.get_weather,
            {
                "name": "get_weather",
                "description": "Fetch real-time weather and temperature for any city.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City or location name (e.g. 'London', 'New York', 'Tokyo')."}
                    },
                    "required": ["location"]
                }
            }
        )
        
        # 6. News
        self.register_tool(
            "get_latest_news",
            self.get_latest_news,
            {
                "name": "get_latest_news",
                "description": "Retrieve current headline news on general topics or specific keywords.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "News topic or keyword (e.g. 'technology', 'world', 'ai')."}
                    }
                }
            }
        )

    async def lookup_wikipedia(self, topic: str) -> Dict[str, Any]:
        """
        Deep Wikipedia lookup: tries direct title summary, and if not exact, uses Wikipedia Search API to find the best matching article.
        """
        headers = {"User-Agent": "JarvisAI/1.0 (https://github.com/jarvis; jarvis@ai.local)"}
        clean_topic = topic.strip()

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                # 1. Try direct page summary
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

                # 2. If direct title didn't hit, use Wikipedia Open Search API
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
        """Live search across global search engines via DuckDuckGo"""
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

    async def fetch_website_content(self, url: str, max_chars: int = 2500) -> Dict[str, Any]:
        """Scrapes and extracts readable text from any global website"""
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=6)) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        # Extract title
                        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
                        title = title_match.group(1).strip() if title_match else url
                        
                        # Strip script and style tags
                        clean = re.sub(r'<(script|style|nav|header|footer).*?>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
                        # Strip HTML tags
                        clean = re.sub(r'<.*?>', ' ', clean)
                        # Collapse whitespace
                        clean = re.sub(r'\s+', ' ', clean).strip()

                        return {
                            "success": True,
                            "url": url,
                            "title": title,
                            "content": clean[:max_chars],
                            "word_count": len(clean.split())
                        }
                    else:
                        return {"success": False, "error": f"Website responded with HTTP status {resp.status}."}
        except Exception as e:
            return {"success": False, "error": f"Could not fetch website content: {str(e)}"}

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

        # Check Wikipedia result
        if isinstance(wiki_res, dict) and wiki_res.get("success") and wiki_res.get("summary"):
            w_title = wiki_res.get("title", clean_q)
            w_summary = wiki_res.get("summary", "")
            w_url = wiki_res.get("url", "")
            
            primary_source = f"Wikipedia ({w_title})"
            if w_url:
                sources.append({"title": f"Wikipedia - {w_title}", "url": w_url})
            
            # Format clean spoken answer (first 2 sentences)
            sentences = re.split(r'(?<=[.!?])\s+', w_summary)
            spoken_answer = " ".join(sentences[:2]) if len(sentences) >= 2 else w_summary
            detailed_answer = f"**{w_title}**\n\n{w_summary}"

        # If Wikipedia is thin or not found, leverage global web results
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
                        return {"error": f"Weather service responded with status {resp.status}"}
        except Exception as e:
            return {"error": f"Could not retrieve weather for {location}: {str(e)}"}

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

research_agent = ResearchAgent()
