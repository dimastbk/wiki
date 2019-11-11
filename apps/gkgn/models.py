from apps import db


class Settlement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gkgn_id = db.Column(db.Integer)
    name = db.Column(db.String(256))
    types = db.Column(db.String(100))
    region = db.Column(db.String(256))
    district = db.Column(db.String(256))

    def __repr__(self):
        return '<Settlement {}>'.format(self.name)


class ATE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gkgn_id = db.Column(db.Integer)
    name = db.Column(db.String(256))
    types = db.Column(db.String(100))
    region = db.Column(db.String(256))

    def __repr__(self):
        return '<ATE {}>'.format(self.name)
