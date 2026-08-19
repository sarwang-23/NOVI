from fastapi import Security


from fastapi_auth0 import Auth0


from app.core.config import settings




auth0 = Auth0(
    domain=settings.AUTH0_DOMAIN,
    api_audience=settings.AUTH0_AUDIENCE,
)




async def get_current_user(user=Security(auth0.get_user)):
    if user is None:
        return None


    return user.model_dump()
