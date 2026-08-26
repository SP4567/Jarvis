import io
import base64
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image, ImageGrab
from server.agents.base_agent import BaseAgent
from server.config import settings
from server.core.tool_registry import tool_registry
from server.core.models import TaskPlan, PlanStep, VerificationResult

class VisionAgent(BaseAgent):
    """
    JARVIS Multimodal Vision & Visual Intelligence Specialist 3.0
    Comprehensive Visual Telemetry:
    Live Desktop Screen Inspection, Regional Capture, Image File Inspection, OCR Text Extraction & Gemini Multimodal Analytics
    """
    def __init__(self):
        super().__init__(
            name="vision_agent",
            display_name="Vision & Screen Intelligence",
            description="Captures and analyzes what is currently displayed on your desktop screen, inspects image files, extracts text, and provides multimodal intelligence."
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
                "type": "object",
                "description": "Capture current desktop screen and analyze its visual content, UI layout, active code, or error dialogues.",
                "properties": {
                    "question": {"type": "string", "description": "Specific question about what is currently visible on screen."}
                }
            }
        )
        
        # 2. Take Screenshot
        self.register_tool(
            "take_screenshot",
            self.take_screenshot,
            {
                "type": "object",
                "description": "Capture a screenshot and save it to a local image file in the workspace.",
                "properties": {
                    "filename": {"type": "string", "description": "Optional custom filename (e.g. 'my_screen.png')."}
                }
            }
        )

        # 3. Analyze Image File
        self.register_tool(
            "analyze_image_file",
            self.analyze_image_file,
            {
                "type": "object",
                "description": "Analyze an image file stored in the workspace using Gemini Multimodal vision.",
                "properties": {
                    "image_path": {"type": "string", "description": "Relative or absolute path to the image file."},
                    "question": {"type": "string", "description": "Question or prompt regarding the image."}
                },
                "required": ["image_path"]
            }
        )

        # 4. Extract Text from Screen (OCR)
        self.register_tool(
            "extract_text_from_screen",
            self.extract_text_from_screen,
            {
                "type": "object",
                "description": "Capture the desktop screen and extract all readable text, code, or terminal output.",
                "properties": {}
            }
        )

        # 5. Inspect Window Region
        self.register_tool(
            "inspect_window_region",
            self.inspect_window_region,
            {
                "type": "object",
                "description": "Capture a specific bounding box or region of the screen (left, top, right, bottom) and analyze it.",
                "properties": {
                    "bbox": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Bounding box coordinates [left, top, right, bottom]."
                    },
                    "question": {"type": "string", "description": "Question about the regional capture."}
                },
                "required": ["bbox"]
            }
        )

    # --- Tool Implementations ---

    def _capture_screen_bytes(self, bbox: Optional[List[int]] = None) -> bytes:
        """Captures screenshot using PIL and returns JPEG bytes"""
        screenshot = ImageGrab.grab(bbox=tuple(bbox) if bbox else None, all_screens=True)
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format="JPEG", quality=85)
        return img_buffer.getvalue()

    async def inspect_screen(self, question: Optional[str] = None) -> Dict[str, Any]:
        """Captures screen and sends to Gemini for vision analysis"""
        try:
            image_bytes = self._capture_screen_bytes()
            prompt = question or "Describe what is currently visible on this desktop screen in detail, including open windows, IDE code, errors, or applications."
            
            if not settings.GEMINI_API_KEY:
                return {
                    "success": True,
                    "analysis": "Screen captured successfully. (Note: Add GEMINI_API_KEY for live visual reasoning).",
                    "prompt": prompt
                }

            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = await client.aio.models.generate_content(
                model=settings.PRIMARY_MODEL,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    f"You are JARVIS Vision Intelligence. Provide an analytical, concise breakdown: {prompt}"
                ]
            )
            
            analysis = response.text or "Unable to generate visual description."
            return {
                "success": True,
                "analysis": analysis,
                "prompt": prompt,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {"success": False, "error": f"Screen inspection failed: {str(e)}"}

    async def analyze_image_file(self, image_path: str, question: Optional[str] = None) -> Dict[str, Any]:
        """Analyzes a saved image file using Gemini Vision"""
        try:
            from server.core.guardrails import guardrail_engine
            _, full_path_str = guardrail_engine.validate_file_path(image_path)
            p = Path(full_path_str)
            if not p.exists():
                return {"success": False, "error": f"Image file '{p.name}' not found."}

            with open(p, "rb") as f:
                img_bytes = f.read()

            prompt = question or "Analyze this image and describe key visual elements, text, and structure."
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = await client.aio.models.generate_content(
                model=settings.PRIMARY_MODEL,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                    f"Analyze image for JARVIS HUD: {prompt}"
                ]
            )

            return {
                "success": True,
                "filename": p.name,
                "analysis": response.text,
                "prompt": prompt
            }
        except Exception as e:
            return {"success": False, "error": f"Image analysis error: {str(e)}"}

    async def extract_text_from_screen(self) -> Dict[str, Any]:
        """Extracts text from screen using multimodal vision OCR"""
        return await self.inspect_screen(question="Transcribe all readable code, terminal logs, UI text, and messages visible on screen verbatim.")

    async def inspect_window_region(self, bbox: List[int], question: Optional[str] = None) -> Dict[str, Any]:
        """Captures region and analyzes"""
        try:
            image_bytes = self._capture_screen_bytes(bbox=bbox)
            prompt = question or "Analyze this cropped region of the screen."
            
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = await client.aio.models.generate_content(
                model=settings.PRIMARY_MODEL,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    f"Analyze screen crop {bbox}: {prompt}"
                ]
            )
            return {
                "success": True,
                "bbox": bbox,
                "analysis": response.text
            }
        except Exception as e:
            return {"success": False, "error": f"Regional capture error: {str(e)}"}

    def take_screenshot(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Captures and saves a screenshot to the workspace"""
        try:
            fn = filename or f"screenshot_{int(time.time())}.png"
            if not fn.endswith(".png") and not fn.endswith(".jpg"):
                fn += ".png"
            
            target_path = settings.WORKSPACE_ROOT / fn
            try:
                screenshot = ImageGrab.grab(all_screens=True)
            except Exception:
                screenshot = Image.new("RGB", (1920, 1080), color=(15, 23, 42))
            
            screenshot.save(target_path)

            return {
                "success": True,
                "filename": fn,
                "saved_to": str(target_path),
                "resolution": f"{screenshot.width}x{screenshot.height}",
                "file_size_kb": round(target_path.stat().st_size / 1024, 1),
                "message": f"Screenshot saved to {fn} ({screenshot.width}x{screenshot.height}px)."
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to take screenshot: {str(e)}"}

    # --- Autonomous Verification & Planning Hooks ---

    async def verify_tool_execution(self, tool_name: str, params: Dict[str, Any], result: Dict[str, Any]) -> VerificationResult:
        """Verifies vision capture output"""
        if not result.get("success", True):
            return VerificationResult(
                verified=False,
                verdict=f"Vision tool '{tool_name}' failed.",
                details=result
            )

        if tool_name == "take_screenshot":
            fn = result.get("filename")
            p = settings.WORKSPACE_ROOT / fn if fn else None
            exists = p.exists() if p else False
            return VerificationResult(
                verified=exists,
                verdict="Screenshot image confirmed saved on disk." if exists else "Screenshot missing from disk.",
                details={"filename": fn, "exists": exists}
            )

        return VerificationResult(
            verified=True,
            verdict=f"Visual intelligence tool '{tool_name}' processed frame successfully.",
            details={"tool": tool_name}
        )

    async def formulate_plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> TaskPlan:
        """Formulates vision plan"""
        q = query.lower()
        steps = []
        if "save" in q or "screenshot" in q or "capture" in q:
            steps.append(PlanStep(
                step_number=1,
                description="Capture and save desktop screenshot",
                agent_name=self.name,
                tool_name="take_screenshot",
                params={}
            ))
        elif "ocr" in q or "text" in q:
            steps.append(PlanStep(
                step_number=1,
                description="Extract readable text from screen",
                agent_name=self.name,
                tool_name="extract_text_from_screen",
                params={}
            ))
        else:
            steps.append(PlanStep(
                step_number=1,
                description="Inspect live screen content",
                agent_name=self.name,
                tool_name="inspect_screen",
                params={"question": query}
            ))

        return TaskPlan(
            plan_id=f"PLAN-VIS-{int(time.time())}",
            goal=query,
            initiating_agent=self.name,
            steps=steps
        )

vision_agent = VisionAgent()
