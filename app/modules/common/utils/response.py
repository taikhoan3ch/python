from typing import Optional, Any, Dict

class StandardResponse:
    @staticmethod
    def success(data: Optional[Any] = None, message: Optional[str] = None) -> Dict:
        return {
            "success": True,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error(message: str, data: Optional[Any] = None) -> Dict:
        return {
            "success": False,
            "message": message,
            "data": data
        } 