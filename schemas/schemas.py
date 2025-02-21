from pydantic import BaseModel
from typing import Dict, Any

class DynamicSchema(BaseModel):
    data: Dict[str, Any]  # Permite cualquier tipo de dato en el cuerpo de la solicitud