def download_file(url, filename=' '):
    try:
        if filename:
            pass
        else:
            filename = req.url[downloadURL.rfind('_')+1:]

        with requests.get(url) as req:
            with open(filename, 'wb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return filename
    except Exception as e:
        print(e)
        return None
