from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository, CategoryRepository
from app.repositories.payment_repository import PaymentRepository, PaymentMethodRepository, PaymentInfoRepository
from app.services.user_service import UserService
from app.services.order_service import OrderService
from app.services.product_service import ProductService, CategoryService
from app.services.payment_service import PaymentService, PaymentMethodService, PaymentInfoService

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_user_service(user_repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repository)

def get_order_repository(db: Session = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)

def get_order_service(order_repository: OrderRepository = Depends(get_order_repository)) -> OrderService:
    return OrderService(order_repository)

def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)

def get_category_repository(db: Session = Depends(get_db)) -> CategoryRepository:
    return CategoryRepository(db)

def get_product_service(
    product_repository: ProductRepository = Depends(get_product_repository),
    category_repository: CategoryRepository = Depends(get_category_repository)
) -> ProductService:
    return ProductService(product_repository, category_repository)

def get_category_service(category_repository: CategoryRepository = Depends(get_category_repository)) -> CategoryService:
    return CategoryService(category_repository)

def get_payment_repository(db: Session = Depends(get_db)) -> PaymentRepository:
    return PaymentRepository(db)

def get_payment_method_repository(db: Session = Depends(get_db)) -> PaymentMethodRepository:
    return PaymentMethodRepository(db)

def get_payment_info_repository(db: Session = Depends(get_db)) -> PaymentInfoRepository:
    return PaymentInfoRepository(db)

def get_payment_service(
    payment_repository: PaymentRepository = Depends(get_payment_repository),
    payment_method_repository: PaymentMethodRepository = Depends(get_payment_method_repository),
    payment_info_repository: PaymentInfoRepository = Depends(get_payment_info_repository)
) -> PaymentService:
    return PaymentService(payment_repository, payment_method_repository, payment_info_repository)

def get_payment_method_service(
    payment_method_repository: PaymentMethodRepository = Depends(get_payment_method_repository)
) -> PaymentMethodService:
    return PaymentMethodService(payment_method_repository)

def get_payment_info_service(
    payment_info_repository: PaymentInfoRepository = Depends(get_payment_info_repository)
) -> PaymentInfoService:
    return PaymentInfoService(payment_info_repository) 