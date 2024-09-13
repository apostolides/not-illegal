from fastapi import FastAPI, Response, status
from fastapi.responses import FileResponse
from urllib.parse import urlparse, parse_qs
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import yt_dlp
import re
import uuid

class youtubeURL(BaseModel):
    url: str

app = FastAPI(docs_url=None)

app.mount("/static", StaticFiles(directory="static"), name="static")

whitelist = ["youtube.com", "m.youtube.com", "youtu.be", "www.youtube.com"]
requiredParameters = ["v"]
allowedPaths = ["/watch"]

def videoQueryIsValid(query):
    return bool(re.match("^[A-Za-z0-9_-]*$", query))

@app.post("/download")
async def do_crime(youtubeURL:youtubeURL, response: Response):
    try:
        parsedUrl = urlparse(youtubeURL.url)
        # print(parsedUrl)
        if parsedUrl.netloc not in whitelist or parsedUrl.path not in allowedPaths:
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            return {"status": "failed", "message":"invalid youtube url."}
        query = parse_qs(parsedUrl.query)
        # print(query)
        if not query["v"] or len(query["v"]) > 1 or not videoQueryIsValid(query["v"][0]):
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            return {"status": "failed", "message":"invalid video parameter."}

        downloadUrl = f"{parsedUrl.netloc}{parsedUrl.path}?v={query["v"][0]}" # Remove other redundant queries.
        outputPath = f"./{str(uuid.uuid4())}"

        ydl_opts = {
            'outtmpl': outputPath,
            'embed-metadata': True,
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(downloadUrl)
            title = meta.get("title", "No Title")

            try:
                duration = meta['formats'][0]['fragments'][0]['duration']
            except:
                duration = 0
            
            if duration == 0 or duration >= 3600:
                response.status_code = status.HTTP_406_NOT_ACCEPTABLE
                return {"status": "failed", "message":"failed to download. Invalid duration."}

            error_code = ydl.download(downloadUrl)

            if error_code:
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return {"status": "failed", "message":"failed to download.", "error_code":error_code}
            else:
                file = f"{outputPath}.m4a"
                Path(file).touch()
                headers = {'Content-Disposition': f'attachment; filename={title}'}
                return FileResponse(file, headers=headers)
                # return {"status": "ok", "message":error_code}
    
    except Exception as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"status": "failed", "message":"failed to parse url."}

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('static/img/favicon.ico')