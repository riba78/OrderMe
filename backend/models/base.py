from extensions import db

class Base(db.Model):
    __abstract__ = True
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns} 