from crewai.tools import BaseTool
import json
import yt_dlp

from pydantic import BaseModel, Field

class YouTubeTrendSearchToolSchema(BaseModel):
    query: str = Field(..., description="The search query or niche topic (e.g., 'AI News', 'Crypto Trends')")

class YouTubeTrendSearchTool(BaseTool):
    name: str = "YouTube Trend Search"
    description: str = (
        "Useful for searching YouTube for trending videos in specific niches. "
        "Input must be a simple string representing the search query or niche topic."
    )
    args_schema: type[BaseModel] = YouTubeTrendSearchToolSchema

    def _run(self, query: str) -> str:
        print(f"DEBUG: Searching YouTube (via yt-dlp) for: {query}")
        
        ydl_opts = {
            'quiet': True,
            'default_search': 'ytsearch5',
            'extract_flat': True, # Don't download, just extract info
            'force_generic_extractor': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # We search for "ytsearch5:query" to get 5 results
                search_query = f"ytsearch5:{query}"
                result = ydl.extract_info(search_query, download=False)
                
                structured_results = []
                if 'entries' in result:
                    for video in result['entries']:
                        structured_results.append({
                            "title": video.get('title'),
                            "url": video.get('url'), # or webpage_url
                            "views": video.get('view_count', 'N/A'),
                            "duration": video.get('duration'),
                            "channel": video.get('uploader')
                        })
                
            return json.dumps(structured_results, indent=2)
            
        except Exception as e:
            # Fallback/Debug info
            return f"Error searching YouTube with yt-dlp: {str(e)}"

if __name__ == "__main__":
    tool = YouTubeTrendSearchTool()
    print(tool._run("Artificial Intelligence"))
