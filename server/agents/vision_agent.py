import io
import base64
import time
from typing import Dict, Any, Optional
from PIL import ImageGrab
from server.agents.base_agent import BaseAgent
from server.config import settings
from server.core.tool_registry import tool_registry

class VisionAgent(BaseAgent):
    """
    JARVIS Multimodal Vision, Screen Inspector & Visual Intelligence Specialist
    """
    def __init__(self):
        super().__init__(
            name="vision_agent",
            display_name="Vision & Screen Intelligence",
            description="Captures and analyzes what is currently displayed on your screen or webcam to assist visually."
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
        # 1. Inspect Screen
        self.register_tool(
            "inspect_screen",
            self.inspect_screen,
            {
                "name": "inspect_screen",
                "description": "Capture current desktop screen and analyze its visual content, UI, code, or active documents.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "Specific question about what is currently visible on screen."}
                    }
                }
            }
        )
        
        # 2. Take Screenshot File
        self.register_tool(
            "take_screenshot",
            self.take_screenshot,
            {
                "name": "take_screenshot",
                "description": "Capture a screenshot and save it to a local image file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string", "description": "Optional custom filename (e.g. 'my_screen.png')."}
                    }
                }
            }
        )

    def take_screenshot(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Saves screenshot to disk"""
        try:
            img = ImageGrab.grab()
            save_name = filename or f"screenshot_{int(time.time())}.png"
            out_path = settings.DATA_DIR / save_name
            img.save(str(out_path), "PNG")
            return {
                "success": True,
                "saved_path": str(out_path),
                "dimensions": f"{img.width}x{img.height}"
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to take screenshot: {str(e)}"}

    async def inspect_screen(self, question: Optional[str] = None) -> Dict[str, Any]:
        """Captures screen and sends to Gemini multimodal model for visual analysis"""
        try:
            img = ImageGrab.grab()
            # Resize image if too massive to optimize latency
            max_size = (1920, 1080)
            img.thumbnail(max_size)
            
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            img_bytes = buf.getvalue()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            prompt_text = question or "Describe what is currently visible on the screen in detail and highlight key UI elements or open windows."
            
            if not settings.GEMINI_API_KEY:
                return {
                    "image_b64_preview": f"data:image/jpeg;base64,{img_b64[:200]}...",
                    "analysis": f"Screen captured successfully ({img.width}x{img.height}). (Note: Add GEMINI_API_KEY to enable AI vision explanations)."
                }

            # Call Gemini Vision via google.genai
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.TEXT_MODEL,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                    prompt_text
                ]
            )
            
            return {
                "question": prompt_text,
                "analysis": response.text,
                "dimensions": f"{img.width}x{img.height}"
            }
        except Exception as e:
            return {"error": f"Screen inspection error: {str(e)}"}

vision_agent = VisionAgent()
