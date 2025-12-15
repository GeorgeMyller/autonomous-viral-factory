from crewai.tools import BaseTool
from youtube_transcript_api import YouTubeTranscriptApi
import json

from pydantic import BaseModel, Field

class YouTubeTranscriptToolSchema(BaseModel):
    video_id: str = Field(..., description="The YouTube Video ID (e.g., 'jNQXAC9IVRw') to fetch the transcript for.")

class YouTubeTranscriptTool(BaseTool):
    name: str = "YouTube Transcript Fetcher"
    description: str = (
        "Useful for getting the full text transcript of a YouTube video. "
        "Input should be a YouTube Video ID (not the full URL, just the ID)."
    )
    args_schema: type[BaseModel] = YouTubeTranscriptToolSchema

    def _run(self, video_id: str) -> str:
        print(f"DEBUG: Fetching transcript for video ID: {video_id}...")
        try:
            api = YouTubeTranscriptApi()
            transcripts = api.list(video_id)
            
            # Priority: Manually created PT -> Manually created EN -> Generated PT -> Generated EN
            # We use a broader list of languages
            languages = ['pt', 'pt-BR', 'en', 'en-US']
            
            transcript = None
            try:
                transcript = transcripts.find_transcript(languages)
            except:
                # Fallback to auto-generated
                try:
                    transcript = transcripts.find_generated_transcript(languages)
                except:
                    # Last resort: just take anything available
                    pass

            if not transcript:
                 # If explicit finding failed, try iterating manually to find ANY proper match
                 # or just take the first one.
                 available_transcripts = list(transcripts)
                 if available_transcripts:
                     transcript = available_transcripts[0]
                 else:
                     return "No transcripts available for this video."

            transcript_data = transcript.fetch()
            
            # Formatter for LLM consumption
            full_text = ""
            for segment in transcript_data:
                start = int(segment.start)
                text = segment.text
                full_text += f"[{start}s] {text}\n"
            
            return full_text[:15000]
            
        except Exception as e:
            return f"Error fetching transcript: {str(e)}"

if __name__ == "__main__":
    tool = YouTubeTranscriptTool()
    # Test with "Python in 100 Seconds" (x7X9w_GIm1s)
    print(tool._run("x7X9w_GIm1s"))
