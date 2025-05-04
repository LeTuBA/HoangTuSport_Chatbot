from agents import Agent, Runner, function_tool
from ..core.config import settings
from ..tools.product_tools import product_search, product_details
from ..prompts.product_agent import PRODUCT_AGENT_PROMPT
from ..core.hooks import CustomAgentHooks
from ..client.spring_client import spring_boot_client
from typing import List, Dict, Any
import traceback
import json
import asyncio

class ProductAgentWrapper:
    """
    Agent xử lý các truy vấn về sản phẩm, tìm kiếm, và đề xuất sản phẩm
    """
    
    def __init__(self):
        """
        Khởi tạo ProductAgent với cấu hình từ settings
        """
        # Tạo hooks cho product agent
        self.hooks = CustomAgentHooks("Product")
        
        # Tạo agent sử dụng OpenAI Agents SDK
        self.agent = Agent(
            name="Product Assistant",
            instructions=PRODUCT_AGENT_PROMPT,
            model=settings.CHAT_MODEL,
            tools=[
                product_search,
                product_details
            ],
            hooks=self.hooks
        )
        
    def _extract_products_from_result(self, result) -> List[Dict[str, Any]]:
        """
        Trích xuất danh sách sản phẩm từ kết quả của agent
        
        Args:
            result: Kết quả từ agent
            
        Returns:
            List[Dict]: Danh sách thông tin sản phẩm
        """
        # Trích xuất từ các tool calls
        products = []
        
        # Lấy sản phẩm từ kết quả tool product_search và product_details
        if hasattr(result, 'tool_calls'):
            for tool_call in result.tool_calls:
                if tool_call.name == 'product_search' and tool_call.output:
                    try:
                        search_results = json.loads(tool_call.output) if isinstance(tool_call.output, str) else tool_call.output
                        if isinstance(search_results, list):
                            products.extend(search_results)
                    except:
                        pass
                
                if tool_call.name == 'product_details' and tool_call.output:
                    try:
                        product_info = json.loads(tool_call.output) if isinstance(tool_call.output, str) else tool_call.output
                        if isinstance(product_info, dict):
                            products.append(product_info)
                    except:
                        pass
                        
        return products
    
    async def process(
        self, 
        message: str, 
        thread_id: str = None, 
        user_id: str = None, 
        auth_token: str = None
    ) -> Dict[str, Any]:
        """
        Xử lý tin nhắn từ người dùng
        
        Args:
            message: Tin nhắn người dùng
            thread_id: ID cuộc trò chuyện
            user_id: ID người dùng
            auth_token: Token xác thực JWT
            
        Returns:
            Dict: Kết quả từ agent
        """
        try:
            # Cập nhật token cho Spring Boot client
            spring_boot_client.update_auth_token(auth_token)
            
            # Sử dụng Runner.run với message
            result = await Runner.run(self.agent, message)
            
            # Trích xuất thông tin sản phẩm từ kết quả
            source_documents = self._extract_products_from_result(result)
            
            # Cấu trúc kết quả để tương thích với API hiện tại
            final_output = result.final_output if hasattr(result, 'final_output') else str(result)
            
            return {
                "message": final_output,
                "thread_id": thread_id,
                "source_documents": source_documents
            }
            
        except Exception as e:
            traceback.print_exc()
            error_msg = f"Xin lỗi, tôi đang gặp sự cố khi xử lý yêu cầu của bạn: {str(e)}"
            # Rút ngắn thông báo lỗi để tránh lỗi MySQL
            if len(error_msg) > 500:
                error_msg = error_msg[:497] + "..."
            
            return {
                "message": error_msg,
                "thread_id": thread_id,
                "source_documents": []
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
        try:
            # Cập nhật token cho Spring Boot client
            spring_boot_client.update_auth_token(auth_token)
            
            # Chuyển đổi lịch sử trò chuyện thành định dạng messages
            context = ""
            if conversation_history and len(conversation_history) > 0:
                context = "Đây là lịch sử trò chuyện trước đó:\n"
                for msg in conversation_history:
                    role = "Người dùng" if msg["role"] == "user" else "Trợ lý"
                    context += f"{role}: {msg['content']}\n"
                context += "\nDựa vào lịch sử trên, hãy trả lời tin nhắn mới này:\n"
            
            # Tạo tin nhắn có ngữ cảnh
            message_with_context = f"{context}{message}" if context else message
            
            # Sử dụng Runner.run với message có ngữ cảnh
            result = await Runner.run(self.agent, message_with_context)
            
            # Trích xuất thông tin sản phẩm từ kết quả
            source_documents = self._extract_products_from_result(result)
            
            # Cấu trúc kết quả để tương thích với API hiện tại
            final_output = result.final_output if hasattr(result, 'final_output') else str(result)
            
            return {
                "message": final_output,
                "thread_id": thread_id,
                "source_documents": source_documents
            }
            
        except Exception as e:
            traceback.print_exc()
            error_msg = f"Xin lỗi, tôi đang gặp sự cố khi xử lý yêu cầu của bạn: {str(e)}"
            # Rút ngắn thông báo lỗi để tránh lỗi MySQL
            if len(error_msg) > 500:
                error_msg = error_msg[:497] + "..."
                
            return {
                "message": error_msg,
                "thread_id": thread_id,
                "source_documents": []
            }

# Singleton instance
product_agent = ProductAgentWrapper()