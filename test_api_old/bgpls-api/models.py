from flask_sqlalchemy import SQLAlchemy
from __main__ import app

db = SQLAlchemy(app)

class BGPLSNeighborship(db.Model):
    __tablename__ = "bgplsneighborship"

    """ Class representing a BGPLS Neighborship """
    exabgp_version = db.Column(db.String)
    time = db.Column(db.String)
    host = db.Column(db.String)
    pid = db.Column(db.Integer)
    ppid = db.Column(db.Integer)
    counter = db.Column(db.Integer)
    local_address = db.Column(db.String, primary_key=True)
    peer_address = db.Column(db.String)
    local_asn = db.Column(db.String)
    peer_asn = db.Column(db.String)
    state_type = db.Column(db.String)
    state_reason = db.Column(db.String)

    def __repr__(self):
        return '<BGPLSNeighborship {}>'.format(self.local_address)

    def as_dict(self):
        return {
            "exabgp": self.exabgp_version,
            "time": self.time,
            "host": self.host,
            "pid": self.pid,
            "ppid": self.ppid,
            "counter": self.counter,
            "neighbor": {
                "address": {
                    "local": self.local_address,
                    "peer": self.peer_address
                },
                "asn": {
                    "local": self.local_asn,
                    "peer": self.peer_asn
                },
                "state": self.state_type,
                "state_reason": self.state_reason
            }
        }
