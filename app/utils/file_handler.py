# app/utils/file_handler.py
import os
from fastapi import UploadFile
from datetime import datetime
import aiofiles
import uuid

async def save_upload_file(upload_file: UploadFile, folder: str) -> str:
    # 저장될 디렉토리 생성
    os.makedirs(folder, exist_ok=True)
    
    # 파일명 생성 (중복 방지를 위해 UUID 사용)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = os.path.splitext(upload_file.filename)[1]
    filename = f"{timestamp}_{uuid.uuid4().hex[:8]}{file_extension}"
    
    file_path = os.path.join(folder, filename)
    
    # 파일 저장
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    
    return file_path