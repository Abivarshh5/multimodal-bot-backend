def success_response(data: dict = None, message: str = None):
    res = {"success": True}
    if data:
        res.update(data)
    if message:
        res["message"] = message
    return res

def error_response(error: str):
    return {"success": False, "error": error}
