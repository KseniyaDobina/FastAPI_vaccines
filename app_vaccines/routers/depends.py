async def pagination_parameters(skip: int = 0, limit: int = 10):
    # Возможно не работает с бд
    return {"skip": skip, "limit": limit}
