from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    name: str
    description: str
    
    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass
