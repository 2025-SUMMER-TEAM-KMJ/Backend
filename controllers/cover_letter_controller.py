from fastapi import APIRouter, Depends

from auth import get_current_user
from services.cover_letter_service import CoverLetterService, get_cover_letter_service

router = APIRouter()

@router.get("/", response_model=None, status_code=200)
def get_cover_letters(type: str, offset: int = 0, limit: int = 20, 
                     service: CoverLetterService = Depends(get_cover_letter_service), 
                     user: dict = Depends(get_current_user)):
    return None

@router.get("/detail/{id}", response_model=None, status_code=200)
def get_cover_letter_detail(id: str, type: str, offset: int = 0, limit: int = 20, 
                     service: CoverLetterService = Depends(get_cover_letter_service), 
                     user: dict = Depends(get_current_user)):
    return None

@router.post("/", response_model=None, status_code=201)
def create_cover_letter(request: CoverLetterRequest, 
                       service: CoverLetterService = Depends(get_cover_letter_service),
                       user: dict = Depends(get_current_user)):
    pass

@router.patch("/search", response_model=None, status_code=200)
def update_cover_letter(request: CoverLetterRequest,
                     service: CoverLetterService = Depends(get_cover_letter_service),
                     user: dict = Depends(get_current_user)):
    return None

@router.delete("/delete/{id}", response_model=None, status_code=200)
def delete_cover_letter(id: str, 
                        service: CoverLetterService = Depends(get_cover_letter_service),
                        user: dict = Depends(get_current_user)):
    return None