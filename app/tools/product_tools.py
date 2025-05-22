from typing import List, Dict, Any, Optional
from ..rag.vector_store import vector_store
from ..client.spring_client import spring_boot_client
from agents import function_tool

def get_product_info(query: str) -> List[Dict]:
    """
    Tìm kiếm thông tin sản phẩm sử dụng Spring Filter
    
    Args:
        query: Filter query (ví dụ: name~'Passion' hoặc price>100000)
        
    Returns:
        Danh sách sản phẩm phù hợp với filter
    """
    return spring_boot_client.search_products(query)

def get_product_by_id(product_id: str) -> Dict:
    """
    Lấy thông tin sản phẩm theo ID
    
    Args:
        product_id: ID sản phẩm
        
    Returns:
        Thông tin sản phẩm nếu tìm thấy, dict rỗng nếu không tìm thấy
    """
    result = spring_boot_client.get_product_by_id(product_id)
    return result if result else {}

def get_products_by_category(category_id: str) -> List[Dict]:
    """
    Lấy danh sách sản phẩm theo danh mục sử dụng Spring Filter
    
    Args:
        category_id: ID hoặc tên danh mục
        
    Returns:
        Danh sách sản phẩm thuộc danh mục
    """
    try:
        print(f"Gọi get_products_by_category với tham số: {category_id}")
        
        # Sử dụng Spring Filter để tìm theo category
        filter_query = f"category.id:{category_id}"
        if not category_id.isdigit():
            filter_query = f"category.name~'{category_id}'"
            
        products = spring_boot_client.search_products(filter_query)
        
        if products:
            print(f"Tìm thấy {len(products)} sản phẩm trong danh mục")
            # Bổ sung thêm thông tin
            for product in products:
                if "category" in product and product["category"]:
                    product["category_name"] = product["category"].get("name", "")
                    product["category_id"] = str(product["category"].get("id", ""))
        else:
            print("Không tìm thấy sản phẩm nào trong danh mục này")
        
        return products
    except Exception as e:
        print(f"Lỗi trong get_products_by_category: {str(e)}")
        return []

def search_products_by_price_range(min_price: float = None, max_price: float = None) -> List[Dict]:
    """
    Tìm kiếm sản phẩm theo khoảng giá sử dụng Spring Filter
    
    Args:
        min_price: Giá tối thiểu
        max_price: Giá tối đa
        
    Returns:
        Danh sách sản phẩm trong khoảng giá
    """
    return spring_boot_client.get_products_by_price_range(min_price, max_price)

@function_tool
def product_search(query: str, top_k: int = None) -> List[Dict[str, Any]]:
    try:
        # Xử lý giá trị mặc định cho top_k bên trong thân hàm
        if top_k is None:
            top_k = 5
            
        # Thử sử dụng vector store (Milvus) để tìm kiếm
        results = vector_store.search(query, top_k=top_k)
        
        # Nếu không tìm thấy kết quả hoặc có lỗi, thử tìm kiếm qua API
        if not results:
            print("Không tìm thấy kết quả từ vector store, chuyển sang tìm kiếm qua API")
            results = spring_boot_client.search_products(f"name~'{query}' or description~'{query}'")
            
        return results
    except Exception as e:
        print(f"Lỗi khi tìm kiếm sản phẩm: {str(e)}")
        # Fallback sang tìm kiếm qua API
        return spring_boot_client.search_products(f"name~'{query}' or description~'{query}'")

@function_tool
def product_details(product_id: str) -> Dict[str, Any]:
    """
    Lấy thông tin chi tiết của sản phẩm từ API
    
    Args:
        product_id: ID của sản phẩm cần lấy thông tin
        
    Returns:
        Thông tin chi tiết sản phẩm hoặc dict rỗng nếu không tìm thấy
    """
    result = spring_boot_client.get_product_by_id(product_id)
    return result if result else {} 

@function_tool("Tìm kiếm sản phẩm theo khoảng giá từ API")
def find_products_by_price_range(min_price: float, max_price: float) -> List[Dict]:
    print(f"Tìm kiếm sản phẩm trong khoảng giá {min_price:,.0f} - {max_price:,.0f} VNĐ từ API")
    results = spring_boot_client.get_products_by_price_range(min_price, max_price)
    
    # Thêm thông tin chi tiết để debug
    if results:
        print(f"Tìm thấy {len(results)} sản phẩm trong khoảng giá từ API")
        # Hiển thị thông tin 2 sản phẩm đầu tiên để debug
        for i, product in enumerate(results[:2]):
            print(f"  {i+1}. {product.get('name', 'Không tên')} - Giá: {product.get('sellPrice', product.get('price', 0)):,.0f} VNĐ")
    else:
        print("Không tìm thấy sản phẩm nào trong khoảng giá yêu cầu")
        
    return results