from sqlalchemy.ext.hybrid import hybrid_property
from app import db

Column = db.Column
Model = db.Model
Relationship = db.relationship


class CurrencyPair(Model):
    __tablename__ = "curpairs"
    id = Column(db.Integer, primary_key=True)
    base_code = Column(db.String(3))
    target_code = Column(db.String(3))

    @hybrid_property
    def code(self):
        return f"{self.base_code}/{self.target_code}"

    @code.setter
    def code(self, value):
        self.base_code, self.target_code = value.split('/')


    def __repr__(self):
        return f"<CurrencyPair #{self.id} '{self.code}'>"


class CurrencyRate(Model):
    __tablename__ = "currates"
    id = Column(db.Integer, primary_key=True)
    date = Column(db.Date)
    rate = Column(db.Float)

    #pair_id = Column(db.Integer, db.ForeignKey("curpairs.id"))
    pair_id = Column(db.Integer, db.ForeignKey(CurrencyPair.id))
    pair = Relationship(CurrencyPair, backref=db.backref("rates", cascade="all,delete", lazy='dynamic'))

    @hybrid_property
    def code(self):
        if self.pair:
            return self.pair.code

    def __repr__(self):
        return f"<CurrencyRate #{self.id} '{self.date} - {self.pair.code} - {self.rate}'>"
