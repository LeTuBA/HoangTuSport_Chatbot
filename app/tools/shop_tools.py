from typing import Dict, Any, List
from agents import function_tool
from ..client.spring_client import spring_boot_client

@function_tool("Lấy thông tin về đơn hàng của người dùng")
def get_user_orders() -> List[Dict[str, Any]]:
    """
    Lấy danh sách đơn hàng của người dùng hiện tại.
    
    Returns:
        Danh sách đơn hàng
    """
    orders = spring_boot_client.get_user_orders()
    return orders

@function_tool("Lấy chi tiết đơn hàng")
def get_order_details(order_id: str) -> Dict[str, Any]:
    """
    Lấy chi tiết của một đơn hàng.
    
    Args:
        order_id: ID của đơn hàng
        
    Returns:
        Chi tiết đơn hàng
    """
    details = spring_boot_client.get_order_details(order_id)
    return details

@function_tool("Lấy thông tin tổng quan về cửa hàng")
def get_shop_info() -> Dict[str, Any]:
    """
    Lấy thông tin tổng quan về cửa hàng Hoàng Tú Pickleball Shop
    
    Returns:
        Thông tin cơ bản về cửa hàng
    """
    return {
        "name": "Hoàng Tú Pickleball Shop",
        "description": "Cửa hàng Hoàng Tú Pickleball Shop chuyên cung cấp các sản phẩm và dịch vụ liên quan đến môn Pickleball chất lượng cao, từ vợt, bóng đến phụ kiện và dịch vụ sửa chữa.",
        "established": "2023",
        "specialty": "Vợt Pickleball, bóng, phụ kiện và dịch vụ sửa chữa",
        "address": "Yên Phong, Bắc Ninh",
        "hours": "8:00 - 22:00 tất cả các ngày trong tuần",
        "phone": "0327 333 333",
        "email": "info@hoangtusport.id.vn",
        "website": "hoangtusport.id.vn",
        "services": [
            "Tư vấn sản phẩm Pickleball",
            "Cung cấp sản phẩm Pickleball",
        ]
    }

@function_tool("Lấy thông tin về vận chuyển và giao hàng")
def get_shipping_info() -> Dict[str, Any]:
    """
    Lấy thông tin về phương thức vận chuyển và giao hàng
    
    Returns:
        Thông tin chi tiết về các phương thức vận chuyển
    """
    return {
        "delivery_options": [
            {"name": "Giao hàng tiêu chuẩn", "time": "Tùy khu vực", "fee": 0},
            {"name": "Giao hàng hỏa tốc (nội thành Bắc Ninh)", "time": "Trong ngày", "fee": 0}
        ],
        "delivery_times": [
            {"area": "Miền Bắc, Hà Nội", "time": "1-2 ngày"},
            {"area": "Miền Nam, TP.HCM", "time": "3-5 ngày"},
            {"area": "Khu vực khác", "time": "2-4 ngày"}
        ],
        "free_shipping": "Miễn phí giao hàng toàn quốc với đơn hàng tiêu chuẩn",
        "delivery_areas": "Giao hàng toàn quốc",
        "note": "Đảm bảo sản phẩm được đóng gói cẩn thận, tránh va đập trong quá trình vận chuyển"
    }


@function_tool("Lấy thông tin liên hệ của cửa hàng")
def get_contact_info() -> Dict[str, Any]:
    """
    Lấy thông tin liên hệ của cửa hàng
    
    Returns:
        Thông tin chi tiết về các kênh liên hệ và địa chỉ cửa hàng
    """
    return {
        "phone": "0327 333 333",
        "email": "info@hoangtusport.id.vn",
        "website": "hoangtusport.id.vn",
        "social_media": {
            "facebook": "facebook.com/hoangtupickleballshop",
            "instagram": "instagram.com/hoangtupickleball"
        },
        "locations": [
            {
                "address": "Yên Phong, Bắc Ninh",
                "phone": "0327 333 333",
                "hours": "8:00 - 22:00 tất cả các ngày trong tuần"
            }
        ]
    }

# Định nghĩa các tools
shop_tools = [
    get_user_orders,
    get_order_details,
    get_shop_info,
    get_shipping_info,
    get_contact_info
] 