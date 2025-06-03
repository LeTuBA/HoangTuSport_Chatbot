from agents import Agent, Runner, function_tool
from ..core.config import settings
from ..tools.cart_tools import (
    get_cart, create_order, get_order_info, 
    get_payment_info, get_my_orders
)
from ..tools.product_tools import get_product_by_id
from ..prompts.checkout_agent import CHECKOUT_AGENT_PROMPT
from ..core.hooks import CustomAgentHooks
from ..client.spring_client import spring_boot_client
from typing import List, Dict, Any, Optional
import json

class CheckoutAgentWrapper:
    """
    Agent xử lý quá trình thanh toán và tạo đơn hàng
    """
    def __init__(self):
        # Tạo hooks cho checkout agent
        self.hooks = CustomAgentHooks("Checkout")
        
        # Tạo agent sử dụng OpenAI Agents SDK
        self.agent = Agent(
            name="Checkout Assistant",
            instructions=CHECKOUT_AGENT_PROMPT,
            model=settings.CHAT_MODEL,
            tools=[
                get_cart,             # Sử dụng trực tiếp get_cart từ cart_tools
                get_product_by_id,    # Lấy thông tin sản phẩm
                create_order,         # Sử dụng trực tiếp create_order từ cart_tools
                get_order_info,       # Lấy thông tin đơn hàng
                get_payment_info,     # Lấy thông tin thanh toán
                get_my_orders         # Lấy danh sách đơn hàng của tôi
            ],
            hooks=self.hooks
        )
    
    async def _is_order_related_query(self, message: str) -> bool:
        """
        Kiểm tra xem tin nhắn có liên quan đến việc xem đơn hàng hay không
        
        Args:
            message: Tin nhắn của người dùng
            
        Returns:
            bool: True nếu tin nhắn liên quan đến xem đơn hàng, False nếu không
        """
        # Các từ khóa liên quan đến việc xem đơn hàng
        order_keywords = [
            "đơn hàng", "lịch sử đơn hàng", "xem đơn", "đơn của tôi", 
            "order", "orders", "đơn đã đặt", "đơn hàng của tôi",
            "đơn của mình", "lịch sử mua hàng", "đơn đã mua", "order history",
            "kiểm tra đơn", "trạng thái đơn"
        ]
        
        message_lower = message.lower()
        for keyword in order_keywords:
            if keyword in message_lower:
                return True
                
        return False
    
    async def process(self, message: str, thread_id: str = None, user_id: str = None, auth_token: str = None):
        """
        Xử lý tin nhắn liên quan đến thanh toán
        
        Args:
            message: Tin nhắn của người dùng
            thread_id: ID cuộc trò chuyện
            user_id: ID người dùng
            auth_token: Token xác thực JWT
        """
        # Cập nhật token cho Spring Boot client
        print(f"Auth token received: {auth_token[:20]}...") if auth_token else print("Auth token is None")
        spring_boot_client.update_auth_token(auth_token)
        
        # Kiểm tra nếu tin nhắn liên quan đến việc xem đơn hàng
        is_order_query = await self._is_order_related_query(message)
        
        # Nếu không phải truy vấn về đơn hàng, kiểm tra giỏ hàng trước khi xử lý
        if not is_order_query:
            # Kiểm tra giỏ hàng trước khi xử lý
            cart = spring_boot_client.get_cart()
            print(f"Checkout Agent - Get Cart Result: {cart}")
            
            if not cart:
                print("Checkout Agent - Cart is None")
                return {
                    "message": "Giỏ hàng của bạn đang trống. Vui lòng thêm sản phẩm vào giỏ hàng trước khi thanh toán.",
                    "source_documents": [],
                    "thread_id": thread_id
                }
                
            if not cart.get("items"):
                print(f"Checkout Agent - Cart items is empty or not found. Cart structure: {cart}")
                return {
                    "message": "Giỏ hàng của bạn đang trống. Vui lòng thêm sản phẩm vào giỏ hàng trước khi thanh toán.",
                    "source_documents": [],
                    "thread_id": thread_id
                }
        else:
            print(f"Checkout Agent - Processing order-related query: {message}")
            
        # Sử dụng Runner để xử lý tin nhắn
        result = await Runner.run(self.agent, message)
        
        # Nếu có order_id trong kết quả, thêm thông tin đơn hàng vào source_documents
        source_documents = []
        if hasattr(result, 'tool_calls'):
            for tool_call in result.tool_calls:
                if tool_call.name in ['create_order', 'get_order_info', 'get_payment_info', 'get_my_orders']:
                    try:
                        order_data = json.loads(tool_call.output)
                        if isinstance(order_data, dict) or isinstance(order_data, list):
                            source_documents.append(order_data)
                    except Exception as e:
                        print(f"Error parsing tool output: {e}")
        
        return {
            "message": result.final_output,
            "source_documents": source_documents,
            "thread_id": thread_id
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
        Xử lý tin nhắn liên quan đến thanh toán với lịch sử trò chuyện
        
        Args:
            message: Tin nhắn của người dùng
            conversation_history: Lịch sử trò chuyện
            thread_id: ID cuộc trò chuyện
            user_id: ID người dùng
            auth_token: Token xác thực JWT
            
        Returns:
            Dict: Kết quả từ agent
        """
        # Cập nhật token cho Spring Boot client
        print(f"Auth token received in process_with_history: {auth_token[:20]}...") if auth_token else print("Auth token is None in process_with_history")
        spring_boot_client.update_auth_token(auth_token)
        
        # Kiểm tra nếu tin nhắn liên quan đến việc xem đơn hàng
        is_order_query = await self._is_order_related_query(message)
        
        # Nếu không phải truy vấn về đơn hàng, kiểm tra giỏ hàng trước khi xử lý
        if not is_order_query:
            # Kiểm tra giỏ hàng trước khi xử lý
            cart = spring_boot_client.get_cart()
            print(f"Checkout Agent (with history) - Get Cart Result: {cart}")
            
            if not cart:
                print("Checkout Agent (with history) - Cart is None")
                return {
                    "message": "Giỏ hàng của bạn đang trống. Vui lòng thêm sản phẩm vào giỏ hàng trước khi thanh toán.",
                    "source_documents": [],
                    "thread_id": thread_id
                }
                
            if not cart.get("items"):
                print(f"Checkout Agent (with history) - Cart items is empty or not found. Cart structure: {cart}")
                return {
                    "message": "Giỏ hàng của bạn đang trống. Vui lòng thêm sản phẩm vào giỏ hàng trước khi thanh toán.",
                    "source_documents": [],
                    "thread_id": thread_id
                }
        else:
            print(f"Checkout Agent (with history) - Processing order-related query: {message}")
        
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
        
        # Sử dụng Runner để xử lý tin nhắn
        result = await Runner.run(self.agent, message_with_context)
        
        # Nếu có order_id trong kết quả, thêm thông tin đơn hàng vào source_documents
        source_documents = []
        if hasattr(result, 'tool_calls'):
            for tool_call in result.tool_calls:
                if tool_call.name in ['create_order', 'get_order_info', 'get_payment_info', 'get_my_orders']:
                    try:
                        order_data = json.loads(tool_call.output)
                        if isinstance(order_data, dict) or isinstance(order_data, list):
                            source_documents.append(order_data)
                    except Exception as e:
                        print(f"Error parsing tool output: {e}")
        
        return {
            "message": result.final_output,
            "source_documents": source_documents,
            "thread_id": thread_id
        }

# Singleton instance
checkout_agent = CheckoutAgentWrapper() 