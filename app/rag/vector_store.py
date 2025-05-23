import os
import logging
from typing import List, Dict, Any, Optional
from langchain_milvus import Milvus
from langchain.schema import Document
from .embeddings import embedding_provider
from ..core.config import settings
from pymilvus import utility, Collection, connections
import traceback

# Cấu hình logging
logger = logging.getLogger(__name__)

class VectorStore:
    """
    Lớp quản lý vector database cho RAG
    """
    def __init__(self):
        self.persist_directory = settings.VECTOR_DB_PATH
        self._ensure_directory()
        self.embedding_function = embedding_provider.model
        
        # Lấy giá trị cấu hình từ settings
        self.uri = settings.MILVUS_URI
        self.collection_name = settings.MILVUS_COLLECTION_NAME
        self.force_recreate = settings.MILVUS_FORCE_RECREATE
        
        logger.info(f"Vector Store được khởi tạo với: uri={self.uri}, collection={self.collection_name}")
        print(f"[MILVUS] Khởi tạo Milvus client với uri={self.uri}, collection={self.collection_name}")
        
        # Kết nối đến Milvus
        self.connection_name = "default"
        self._connect_to_milvus()
        
        # Khởi tạo vector store
        self._init_vector_store()
    
    def _ensure_directory(self):
        """
        Đảm bảo thư mục tồn tại
        """
        os.makedirs(self.persist_directory, exist_ok=True)
        logger.info(f"Thư mục {self.persist_directory} đã được tạo hoặc đã tồn tại")
        
    def _connect_to_milvus(self):
        """
        Kết nối đến Milvus server
        """
        try:
            logger.info(f"Kết nối tới Milvus server: {self.uri}")
            print(f"[MILVUS] Kết nối tới Milvus server: {self.uri}")
            
            # Đảm bảo URI có định dạng đúng (http://host:port)
            connections.connect(
                alias=self.connection_name,
                uri=self.uri
            )
        except Exception as e:
            logger.error(f"Lỗi kết nối đến Milvus: {str(e)}")
            print(f"[MILVUS] Lỗi kết nối đến Milvus: {str(e)}")
            traceback.print_exc()
            raise
    
    def _check_collection_exists(self) -> bool:
        """
        Kiểm tra xem collection đã tồn tại chưa
        """
        try:
            # Sử dụng PyMilvus utility để kiểm tra collection
            exists = utility.has_collection(self.collection_name)
            logger.info(f"Kiểm tra collection '{self.collection_name}': {'Tồn tại' if exists else 'Không tồn tại'}")
            print(f"[MILVUS] Kiểm tra collection '{self.collection_name}': {'Tồn tại' if exists else 'Không tồn tại'}")
            return exists
        except Exception as e:
            logger.error(f"Lỗi kiểm tra collection: {str(e)}")
            print(f"[MILVUS] Lỗi kiểm tra collection: {str(e)}")
            return False
    
    def _init_vector_store(self):
        """
        Khởi tạo vector store
        """
        try:
            logger.info(f"Khởi tạo Langchain Milvus vector store với collection '{self.collection_name}'")
            print(f"[MILVUS] Khởi tạo Langchain Milvus vector store với collection '{self.collection_name}'")
            
            # Kiểm tra collection tồn tại
            exists = self._check_collection_exists()
            
            # Xóa collection cũ nếu force_recreate=True
            if exists and self.force_recreate:
                logger.info(f"Xóa collection '{self.collection_name}' cũ theo yêu cầu force_recreate")
                print(f"[MILVUS] Xóa collection '{self.collection_name}' cũ theo yêu cầu force_recreate")
                utility.drop_collection(self.collection_name)
                exists = False
            
            # Tạo mới collection nếu chưa tồn tại
            if not exists:
                logger.info(f"Collection '{self.collection_name}' không tồn tại. Đang tạo mới...")
                print(f"[MILVUS] Collection '{self.collection_name}' không tồn tại. Đang tạo mới...")
                
                # Sử dụng langchain_milvus để tạo vector store mới
                # Kết nối đã được thiết lập ở trên, chỉ cần chỉ định connection_args cho rõ ràng
                connection_args = {"uri": self.uri}
                
                self.vector_store = Milvus(
                    embedding_function=self.embedding_function,
                    collection_name=self.collection_name,
                    connection_args=connection_args,
                    auto_id=True  # Tự động tạo ID cho văn bản
                )
                
                print(f"[MILVUS] Đã tạo mới collection '{self.collection_name}' thành công")
            else:
                # Kết nối đến collection đã tồn tại
                connection_args = {"uri": self.uri}
                
                self.vector_store = Milvus(
                    embedding_function=self.embedding_function,
                    collection_name=self.collection_name,
                    connection_args=connection_args,
                    auto_id=True  # Tự động tạo ID cho văn bản
                )
            
            logger.info("Vector store đã sẵn sàng")
            print("[MILVUS] Vector store đã sẵn sàng")
        except Exception as e:
            logger.error(f"Lỗi khởi tạo vector store: {str(e)}")
            print(f"[MILVUS] Lỗi khởi tạo vector store: {str(e)}")
            traceback.print_exc()
            raise
    
    def drop_and_recreate_collection(self):
        """
        Xóa collection hiện tại và tạo lại collection mới
        
        Returns:
            bool: True nếu xóa và tạo lại thành công, False nếu có lỗi
        """
        try:
            logger.info(f"Bắt đầu xóa và tạo lại collection '{self.collection_name}'")
            print(f"[MILVUS] Bắt đầu xóa và tạo lại collection '{self.collection_name}'")
            
            # Kiểm tra collection có tồn tại không
            exists = self._check_collection_exists()
            
            # Nếu tồn tại thì xóa
            if exists:
                try:
                    logger.info(f"Xóa collection '{self.collection_name}' hiện tại")
                    print(f"[MILVUS] Xóa collection '{self.collection_name}' hiện tại")
                    utility.drop_collection(self.collection_name)
                except Exception as e:
                    # Ghi log lỗi nhưng không dừng lại
                    logger.warning(f"Không thể xóa collection: {str(e)}")
                    print(f"[MILVUS] Cảnh báo: Không thể xóa collection: {str(e)}")
                    print(f"[MILVUS] Tiếp tục thử tạo lại collection mà không xóa")
            
            # Dù xóa thành công hay không, vẫn thử tạo lại vector store
            connection_args = {"uri": self.uri}
            
            # Thử kết nối lại trước khi tạo collection mới
            try:
                # Đóng kết nối cũ nếu có
                connections.disconnect(self.connection_name)
                logger.info("Đã đóng kết nối cũ")
                print("[MILVUS] Đã đóng kết nối cũ")
            except:
                # Bỏ qua lỗi nếu không thể đóng kết nối
                pass
                
            # Kết nối lại
            logger.info("Kết nối lại với Milvus...")
            print("[MILVUS] Kết nối lại với Milvus...")
            self._connect_to_milvus()
            
            # Thử tạo vector store mới
            logger.info("Tạo vector store mới...")
            print("[MILVUS] Tạo vector store mới...")
            self.vector_store = Milvus(
                embedding_function=self.embedding_function,
                collection_name=self.collection_name,
                connection_args=connection_args,
                auto_id=True
            )
            
            logger.info(f"Đã tạo lại collection '{self.collection_name}' thành công")
            print(f"[MILVUS] Đã tạo lại collection '{self.collection_name}' thành công")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi xóa và tạo lại collection: {str(e)}")
            print(f"[MILVUS] Lỗi khi xóa và tạo lại collection: {str(e)}")
            traceback.print_exc()
            return False
    
    def add_documents(self, documents: List[Document]):
        """
        Thêm tài liệu vào vector store
        """
        try:
            # Tạo IDs cho documents nếu cần
            ids = [str(i) for i in range(len(documents))]
            self.vector_store.add_documents(documents, ids=ids)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi thêm tài liệu: {str(e)}")
            return False
    
    def add_products(self, products: List[Dict[str, Any]]):
        """
        Thêm các sản phẩm vào vector database
        """
        logger.info(f"Bắt đầu thêm {len(products) if products else 0} sản phẩm vào vector database")
        print(f"[MILVUS] Bắt đầu thêm {len(products) if products else 0} sản phẩm vào vector database")
        
        if not products:
            logger.warning("Không có sản phẩm nào để thêm vào vector database")
            print("[MILVUS] Không có sản phẩm nào để thêm vào vector database")
            return
        
        try:    
            documents = []
            ids = [] # Danh sách IDs cho documents
            
            for idx, product in enumerate(products):
                try:
                    # Lấy ID của sản phẩm để log
                    product_id = product.get("id", "không có ID")
                    
                    # Tạo văn bản phong phú từ thông tin sản phẩm bằng tiếng Anh
                    product_text = f"Product {product.get('name', '')} with product code {product.get('id', '')}. "
                    product_text += f"Description: {product.get('description', '')}. "
                    product_text += f"Selling price: {product.get('sellPrice', product.get('price', 0))} $ (USD). "
                    
                    if product.get('quantity') is not None:
                        product_text += f"Stock quantity: {product.get('quantity')}. "
                    
                    if product.get('status') is not None:
                        product_text += f"Status: {product.get('status')}. "
                    
                    if product.get('category') is not None:
                        product_text += f"Category: {product.get('category', {}).get('name', '')}. "
                    
                    # Thêm thông tin nhà cung cấp nếu có
                    if product.get('supplier') is not None:
                        product_text += f"Supplier: {product.get('supplier', {}).get('name', '')}. "
                    
                    # Log mẫu cho vài sản phẩm đầu tiên
                    if idx < 2:
                        logger.info(f"Mẫu sản phẩm {product_id}: {product_text[:100]}...")
                        print(f"[MILVUS] Mẫu sản phẩm {product_id}: {product_text[:100]}...")
                    
                    # Tạo document với metadata
                    doc = Document(
                        page_content=product_text,
                        metadata={
                            "product_id": str(product.get("id", "")),  # Đảm bảo ID dạng string
                            "name": product.get("name", ""),
                            "price": float(product.get("sellPrice", product.get("price", 0))),
                            "image_url": product.get("image", product.get("imageUrl", "")),
                            "category": product.get("category", {}).get("name", ""),
                            "status": product.get("status", ""),
                            "quantity": int(product.get("quantity", 0)),
                            "supplier_name": product.get("supplier", {}).get("name", ""),
                            "created_at": str(product.get("createdAt", "")),
                            "updated_at": str(product.get("updatedAt", ""))
                        }
                    )
                    documents.append(doc)
                    
                    # Tạo ID cho document (sử dụng ID sản phẩm nếu có hoặc tạo mới)
                    doc_id = f"product_{product.get('id', str(idx))}"
                    ids.append(doc_id)
                    
                except Exception as e:
                    logger.error(f"Lỗi khi xử lý sản phẩm {product.get('id', 'không có ID')}: {str(e)}")
                    print(f"[MILVUS] Lỗi khi xử lý sản phẩm {product.get('id', 'không có ID')}: {str(e)}")
                    # Tiếp tục với sản phẩm tiếp theo
            
            if not documents:
                logger.warning("Không có documents nào được tạo từ sản phẩm")
                print("[MILVUS] Không có documents nào được tạo từ sản phẩm")
                return
                
            logger.info(f"Đã chuẩn bị {len(documents)} documents để thêm vào collection '{self.collection_name}'")
            print(f"[MILVUS] Đã chuẩn bị {len(documents)} documents để thêm vào collection '{self.collection_name}'")
            
            # Thêm documents vào vector database với IDs
            self.vector_store.add_documents(documents, ids=ids)
            
            logger.info(f"Đã thêm thành công {len(documents)} documents vào collection '{self.collection_name}'")
            print(f"[MILVUS] Đã thêm thành công {len(documents)} documents vào collection '{self.collection_name}'")
            
        except Exception as e:
            error_msg = f"Lỗi khi thêm sản phẩm vào vector database: {str(e)}"
            logger.error(error_msg)
            print(f"[MILVUS] {error_msg}")
            traceback.print_exc()
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Tìm kiếm trong vector store
        """
        try:
            results = self.vector_store.similarity_search_with_score(query, k=top_k)
            
            # Chuyển đổi kết quả sang định dạng dễ sử dụng
            formatted_results = []
            for doc, score in results:
                item = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                }
                formatted_results.append(item)
            
            return formatted_results
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm: {str(e)}")
            return []

# Singleton instance
vector_store = VectorStore() 