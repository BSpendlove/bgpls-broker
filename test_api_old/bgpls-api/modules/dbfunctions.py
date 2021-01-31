from app import app, db
from modules.parsers.exabgp_parser import parse_neighbor_state
from models import (
    BGPLSNeighborship
)

def handle_bgp_state(message):
    """Adds BGP State to database"""
    neighbor = BGPLSNeighborship(**parse_neighbor_state(message))
    existing_neighbor = BGPLSNeighborship.query.get(neighbor.local_address)
    if existing_neighbor:
        if neighbor.state_type == "down":
            app.logger.debug("Neighbor {} down, removing from database...".format(neighbor.local_address))
            existing_neighbor.delete()
        else:
            app.logger.debug("Existing neighbor state for {} in database...".format(neighbor.local_address))
            return None

    db.session.add(neighbor)
    db.session.commit()
    app.logger.debug("Added BGPLSNeighborship: {}".format(neighbor))
    return neighbor