from apps import db


class Settlement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gkgn_id = db.Column(db.Integer)
    name = db.Column(db.String(256))
    okato_name = db.Column(db.String(256))
    oktmo_name = db.Column(db.String(256))
    types = db.Column(db.String(100))
    region = db.Column(db.String(256))
    district = db.Column(db.String(256))
    c_lat = db.Column(db.Float(precision=6))
    c_lon = db.Column(db.Float(precision=6))
    okato = db.Column(db.String(11))
    oktmo = db.Column(db.String(11))
    oktmo_up = db.Column(db.String(11))

    def __repr__(self):
        return '<Settlement {}>'.format(self.name)


class ATE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gkgn_id = db.Column(db.Integer)
    name = db.Column(db.String(256))
    okato_name = db.Column(db.String(256))
    oktmo_name = db.Column(db.String(256))
    types = db.Column(db.String(100))
    region = db.Column(db.String(256))
    okato = db.Column(db.String(11))
    oktmo = db.Column(db.String(11))
    oktmo_up = db.Column(db.String(11))

    def __repr__(self):
        return '<ATE {}>'.format(self.name)
