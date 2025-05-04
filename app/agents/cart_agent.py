from agents import Agent, Runner, function_tool
from ..core.config import settings
from ..tools.cart_tools import add_to_cart, update_cart, remove_from_cart, get_cart, clear_cart
from ..tools.product_tools import product_search, product_details
from ..prompts.cart_agent import CART_AGENT_PROMPT
from ..core.hooks import CustomAgentHooks
from typing import List, Dict, Any
import asyncio
import json

class CartAgentWrapper:
    """
    Agent xử lý các yêu cầu về giỏ hàng và thanh toán
    """
    def __init__(self):
        # Tạo hooks cho cart agent
        self.hooks = CustomAgentHooks("Cart")
        
        # Tạo agent sử dụng OpenAI Agents SDK
        self.agent = Agent(
            name="Cart Assistant",
            instructions=CART_AGENT_PROMPT,
            model=settings.CHAT_MODEL,
            tools=[
                product_search,
                product_details,
                add_to_cart,
                update_cart,
                remove_from_cart,
                get_cart,
                clear_cart
            ],
            hooks=self.hooks
        )
    
    def _extract_products_from_result(self, result: Any) -> List[Dict[str, Any]]:
        """
        Trích xuất thông tin sản phẩm từ kết quả của tool
        
        Args:
            result: Kết quả từ tool
            
        Returns:
            List[Dict]: Danh sách thông tin sản phẩm
        """
        products = []
        
        # Lấy sản phẩm từ kết quả tool search_products và get_product_details
        if hasattr(result, 'tool_calls'):
            for tool_call in result.tool_calls:
                if tool_call.name in ['product_search', 'product_details'] and tool_call.output:
                    try:
                        product_data = json.loads(tool_call.output)
                        if isinstance(product_data, list):
                            products.extend(product_data)
                        elif isinstance(product_data, dict):
                            products.append(product_data)
                    except:
                        pass
                        
        return products
    
    async def process(self, message: str, thread_id: str = None, user_id: str = None, auth_token: str = None):
        """
        Xử lý tin nhắn từ người dùng
        
        Args:
            message: Tin nhắn người dùng
            thread_id: ID cuộc trò chuyện
            user_id: ID người dùng
            auth_token: Token xác thực JWT
        """
        # Cập nhật token cho Spring Boot client
        from ..client.spring_client import spring_boot_client
        spring_boot_client.update_auth_token(auth_token)
        
        # Sử dụng Runner từ OpenAI Agents SDK để xử lý tin nhắn
        result = await Runner.run(self.agent, message)
        
        # Trích xuất thông tin sản phẩm từ kết quả của tool
        source_documents = self._extract_products_from_result(result)
        
        # Cấu trúc kết quả để tương thích với API hiện tại
        return {
            "message": result.final_output,
            "thread_id": thread_id,
            "source_documents": source_documents
        }
        
    async def process_with_history(
        self, 
        message: str, 
        conversation_history: List[Dict[str, Any]], 
        thread_id: str = None, 
        user_id: str = None, 
        auth_token: str = None
    ) -> Dict[str, Any]:
        """
        Xử lý tin nhắn từ người dùng với lịch sử trò chuyện
        
        Args:
            message: Tin nhắn người dùng
            conversation_history: Lịch sử trò chuyện
            thread_id: ID cuộc trò chuyện
            user_id: ID người dùng
            auth_token: Token xác thực JWT
            
        Returns:
            Dict: Kết quả từ agent
        """
        # Cập nhật token cho Spring Boot client
        from ..client.spring_client import spring_boot_client
        spring_boot_client.update_auth_token(auth_token)
        
        # Chuẩn bị ngữ cảnh từ lịch sử trò chuyện
        context = ""
        if conversation_history and len(conversation_history) > 0:
            context = "Đây là lịch sử trò chuyện trước đó:\n"
            for msg in conversation_history:
                role = "Người dùng" if msg["role"] == "user" else "Trợ lý"
                context += f"{role}: {msg['content']}\n"
            context += "\nDựa vào lịch sử trên, hãy trả lời tin nhắn mới này:\n"
        
        # Tạo tin nhắn với ngữ cảnh
        message_with_context = f"{context}{message}" if context else message
        
        # Sử dụng Runner từ OpenAI Agents SDK để xử lý tin nhắn
        result = await Runner.run(self.agent, message_with_context)
        
        # Trích xuất thông tin sản phẩm từ kết quả của tool
        source_documents = self._extract_products_from_result(result)
        
        # Cấu trúc kết quả để tương thích với API hiện tại
        return {
            "message": result.final_output,
            "thread_id": thread_id,
            "source_documents": source_documents
        }

# Singleton instance
cart_agent = CartAgentWrapper() 