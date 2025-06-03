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

@function_tool
def get_product_details(product_id: str) -> str:
    """
    Lấy thông tin chi tiết của sản phẩm
    
    Args:
        product_id: ID của sản phẩm
    """
    result = get_product_by_id(product_id)
    return json.dumps(result)

@function_tool
def get_order_details(order_id: str) -> str:
    """
    Lấy thông tin chi tiết của đơn hàng
    
    Args:
        order_id: ID của đơn hàng
    """
    result = get_order_info(order_id)
    return json.dumps(result)

@function_tool
def get_payment_details(order_id: str) -> str:
    """
    Lấy thông tin thanh toán của đơn hàng
    
    Args:
        order_id: ID của đơn hàng
    """
    result = get_payment_info(order_id)
    return json.dumps(result)

@function_tool
def list_my_orders() -> str:
    """
    Lấy danh sách đơn hàng của người dùng
    """
    result = get_my_orders()
    return json.dumps(result)

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
                get_product_details,  # Lấy thông tin sản phẩm
                create_order,         # Sử dụng trực tiếp create_order từ cart_tools
                get_order_details,    # Lấy thông tin đơn hàng
                get_payment_details,  # Lấy thông tin thanh toán
                list_my_orders       # Lấy danh sách đơn hàng của tôi
            ],
            hooks=self.hooks
        )
    
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
            
        # Sử dụng Runner để xử lý tin nhắn
        print(f"Checkout Agent - Processing message with cart: {cart}")
        result = await Runner.run(self.agent, message)
        
        # Nếu có order_id trong kết quả, thêm thông tin đơn hàng vào source_documents
        source_documents = []
        if hasattr(result, 'tool_calls'):
            for tool_call in result.tool_calls:
                if tool_call.name in ['create_order', 'get_order_details', 'get_payment_details']:
                    try:
                        order_data = json.loads(tool_call.output)
                        if isinstance(order_data, dict):
                            source_documents.append(order_data)
                    except:
                        pass
        
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
                if tool_call.name in ['create_order', 'get_order_details', 'get_payment_details']:
                    try:
                        order_data = json.loads(tool_call.output)
                        if isinstance(order_data, dict):
                            source_documents.append(order_data)
                    except:
                        pass
        
        return {
            "message": result.final_output,
            "source_documents": source_documents,
            "thread_id": thread_id
        }

# Singleton instance
checkout_agent = CheckoutAgentWrapper() 