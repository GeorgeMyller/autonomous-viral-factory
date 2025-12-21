"""
Viral Moment Analyzer Tool

Analyzes video transcripts to identify the most viral-worthy segments.
Uses Whisper for transcription and LLM for moment identification.
"""
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
import json
import tempfile
from typing import Optional
from pathlib import Path


class ViralMomentAnalyzerSchema(BaseModel):
    file_path: str = Field(..., description="Path to the video file to analyze.")


class ViralMoment(BaseModel):
    """Represents a single viral moment identified in a video."""
    rank: int
    start_time: str  # Format: "MM:SS"
    end_time: str    # Format: "MM:SS"
    text: str        # The transcript text of this moment
    viral_score: float  # 0.0 to 1.0
    reasoning: str   # Why this moment is viral-worthy


class ViralMomentAnalyzerTool(BaseTool):
    name: str = "Viral Moment Analyzer"
    description: str = (
        "Analyzes a video file to identify the most viral-worthy moments. "
        "Returns a list of suggested clips with precise timestamps, ranked by viral potential. "
        "Input should be the path to a downloaded video file."
    )
    args_schema: type[BaseModel] = ViralMomentAnalyzerSchema
    
    # Allow configuration of LLM provider
    llm_provider: str = "openai"
    model_name: str = "gpt-4o"
    
    def _run(self, file_path: str) -> str:
        """
        Main execution flow:
        1. Transcribe video with Whisper (with timestamps)
        2. Send transcript to LLM for viral moment analysis
        3. Return ranked list of moments with timestamps
        """
        print(f"DEBUG: Analyzing video for viral moments: {file_path}")
        
        if not os.path.exists(file_path):
            return f"Error: Video file not found at {file_path}"
        
        # Step 1: Transcribe with Whisper
        try:
            transcript_with_timestamps = self._transcribe_with_whisper(file_path)
            if not transcript_with_timestamps:
                return "Error: Failed to transcribe video"
            print(f"DEBUG: Transcription complete, length: {len(transcript_with_timestamps)} chars")
        except Exception as e:
            return f"Error transcribing video: {str(e)}"
        
        # Step 2: Analyze with LLM
        try:
            viral_moments = self._analyze_with_llm(transcript_with_timestamps)
            print(f"DEBUG: Analysis complete, found {len(viral_moments)} moments")
        except Exception as e:
            return f"Error analyzing transcript: {str(e)}"
        
        # Step 3: Return results as JSON
        return json.dumps(viral_moments, indent=2)
    
    def _transcribe_with_whisper(self, video_path: str) -> str:
        """
        Transcribe video using OpenAI Whisper (local model).
        Returns transcript with timestamps in format: [MM:SS] text
        """
        import whisper
        
        print("DEBUG: Loading Whisper model (base)...")
        model = whisper.load_model("base")
        
        print("DEBUG: Transcribing audio...")
        result = model.transcribe(video_path, verbose=False)
        
        # Format with timestamps
        formatted_transcript = ""
        for segment in result.get("segments", []):
            start_seconds = int(segment["start"])
            minutes = start_seconds // 60
            seconds = start_seconds % 60
            text = segment["text"].strip()
            formatted_transcript += f"[{minutes:02d}:{seconds:02d}] {text}\n"
        
        # Also save as SRT for later use
        self._save_srt(result, video_path)
        
        return formatted_transcript
    
    def _save_srt(self, whisper_result: dict, video_path: str) -> str:
        """Save transcription as SRT file for subtitle burning."""
        srt_path = Path(video_path).with_suffix('.srt')
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(whisper_result.get("segments", []), 1):
                start = self._seconds_to_srt_time(segment["start"])
                end = self._seconds_to_srt_time(segment["end"])
                text = segment["text"].strip()
                f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
        
        print(f"DEBUG: SRT saved to {srt_path}")
        return str(srt_path)
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _normalize_timestamp(self, timestamp) -> str:
        """
        Normalize any timestamp format to MM:SS.
        Handles: float (12.3), int (12), string "12.3", string "00:12", string "00:12.3"
        """
        if timestamp is None:
            return "00:00"
        
        # If it's already a string in MM:SS format, validate and return
        if isinstance(timestamp, str):
            timestamp = timestamp.strip()
            
            # Handle MM:SS or HH:MM:SS format
            if ":" in timestamp:
                parts = timestamp.split(":")
                try:
                    if len(parts) == 2:
                        mins = int(parts[0])
                        secs = int(float(parts[1]))  # Handle "00:12.3" -> "00:12"
                        return f"{mins:02d}:{secs:02d}"
                    elif len(parts) == 3:
                        # HH:MM:SS -> MM:SS (for clips under 1hr)
                        hours = int(parts[0])
                        mins = int(parts[1]) + hours * 60
                        secs = int(float(parts[2]))
                        return f"{mins:02d}:{secs:02d}"
                except ValueError:
                    pass
            
            # Try parsing as raw seconds
            try:
                total_seconds = float(timestamp)
                mins = int(total_seconds // 60)
                secs = int(total_seconds % 60)
                return f"{mins:02d}:{secs:02d}"
            except ValueError:
                return "00:00"
        
        # Handle numeric types (int, float)
        if isinstance(timestamp, (int, float)):
            total_seconds = float(timestamp)
            mins = int(total_seconds // 60)
            secs = int(total_seconds % 60)
            return f"{mins:02d}:{secs:02d}"
        
        return "00:00"
    
    def _analyze_with_llm(self, transcript: str) -> list[dict]:
        """
        Use LLM to identify viral moments in the transcript.
        Supports multiple providers: OpenAI, Gemini, Ollama.
        Returns list of moments with timestamps and reasoning.
        """
        from dotenv import load_dotenv
        import litellm
        
        load_dotenv()
        
        # Determine model string based on provider
        if self.llm_provider == "gemini":
            model = f"gemini/{self.model_name}" if not self.model_name.startswith("gemini/") else self.model_name
        elif self.llm_provider == "ollama":
            model = f"ollama/{self.model_name}" if not self.model_name.startswith("ollama/") else self.model_name
        else:
            model = self.model_name  # OpenAI or other
        
        print(f"DEBUG: Using LLM provider={self.llm_provider}, model={model}")
        
        prompt = f"""You are a viral content expert. Analyze this video transcript and identify the TOP 3 moments that would make the best short-form viral clips (30-60 seconds each).

For each moment, consider:
- Emotional impact (surprise, humor, inspiration, controversy)
- Strong hooks (attention-grabbing statements)
- Shareable quotes or insights
- Revelations or "aha" moments
- Prioritize ANSWERS and INSIGHTS over questions

TRANSCRIPT (with timestamps in [MM:SS] format):
{transcript[:12000]}

Return ONLY a valid JSON object with a "moments" array containing exactly 3 moments, each with:
- rank (1-3, where 1 is the most viral)
- start_time (format: "MM:SS" - use the timestamp from the transcript)
- end_time (format: "MM:SS" - approximately 30-60 seconds after start)
- text (the actual transcript text of this moment, max 100 chars)
- viral_score (0.0 to 1.0)
- reasoning (brief explanation of why this is viral-worthy)

Example format:
{{"moments": [
  {{"rank": 1, "start_time": "02:15", "end_time": "03:00", "text": "...", "viral_score": 0.95, "reasoning": "..."}}
]}}"""

        try:
            response = litellm.completion(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a viral content analyst. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            print(f"DEBUG: LLM response length: {len(result_text)} chars")
            
            # Clean up markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            
            # Handle various response formats
            moments = []
            if isinstance(result, dict) and "moments" in result:
                moments = result["moments"]
            elif isinstance(result, list):
                moments = result
            else:
                # Try to find any list in the result
                for key, value in result.items():
                    if isinstance(value, list):
                        moments = value
                        break
            
            # Normalize all timestamps to MM:SS format
            normalized_moments = []
            for moment in moments:
                normalized = moment.copy()
                normalized["start_time"] = self._normalize_timestamp(moment.get("start_time", "00:00"))
                normalized["end_time"] = self._normalize_timestamp(moment.get("end_time", "00:30"))
                normalized_moments.append(normalized)
            
            return normalized_moments
                
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse LLM response: {e}")
            print(f"Response was: {result_text[:500] if 'result_text' in dir() else 'N/A'}")
            return []
        except Exception as e:
            print(f"ERROR: LLM call failed: {e}")
            raise


if __name__ == "__main__":
    # Test the tool
    import sys
    
    tool = ViralMomentAnalyzerTool()
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        # Default test path
        video_path = "downloads/test_video.mp4"
    
    print(f"Testing ViralMomentAnalyzerTool with: {video_path}")
    result = tool._run(video_path)
    print("Result:")
    print(result)
