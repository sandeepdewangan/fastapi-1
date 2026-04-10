from fastapi import APIRouter

router =  APIRouter()


@router.get("/auth")
def get_users():
    return {'user': 'Sandeep'}