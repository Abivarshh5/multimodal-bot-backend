from fastapi import Request
from fastapi.responses import JSONResponse

async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    print("error handler")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc), "message": "Internal Server Error"},
    )

def setup_error_handlers(app):
    app.add_exception_handler(Exception, global_exception_handler)
