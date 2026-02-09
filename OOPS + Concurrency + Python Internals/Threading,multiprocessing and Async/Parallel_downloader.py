import asyncio
import aiohttp
from pathlib import Path
from urllib.parse import urlparse

dur=Path("downloads")
dur.mkdir(exist_ok=True)

chunk_size=1024*32  

def get_filename(url,index):
    path=urlparse(url).path
    name=Path(path).name
    return name if name else f"file_{index}"

async def download_file(session,url,index):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            total_size=int(response.headers.get("Content-Length", 0))
            downloaded=0

            filename=get_filename(url,index)
            file_path=dur/filename

            with open(file_path,"wb") as f:
                async for chunk in response.content.iter_chunked(chunk_size):
                    f.write(chunk)
                    downloaded+= len(chunk)

                    if total_size:
                        percent = (downloaded / total_size) * 100
                        print(f"{filename}: {percent:.2f}% downloaded", end="\r")

            print(f"{filename}: Download complete")

    except Exception as e:
        print(f"Failed to download {url} | Error: {e}")


async def main(urls):
    timeout=aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks=[download_file(session, url, i + 1) for i, url in enumerate(urls)]
        await asyncio.gather(*tasks)

print("Parallel file downloader")
print("Enter URLs to download (type '0' to finish):")
urls=[]
while True:
    url = input(">Link:  ").strip()
    if url.lower()=="done":
        break
    if url:
        urls.append(url)

if not urls:
    print("No URLs provided.")
else:
    asyncio.run(main(urls))
    print("All downloads finished.")
