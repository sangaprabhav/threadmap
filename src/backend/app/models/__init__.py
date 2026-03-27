"""Canonical intelligence schema — the core data model of ThreadMap.

Object hierarchy:
  Source → Actor → Content → MediaAsset
  Content → Claim → Entity
  Content → NarrativeCluster
  Alert → Case
  Edge connects any two objects

Every object carries provenance metadata via the ProvenanceMixin.
"""

from app.models.base import Base
from app.models.provenance import ProvenanceMixin
from app.models.source import Source
from app.models.actor import Actor
from app.models.content import Content
from app.models.media_asset import MediaAsset
from app.models.claim import Claim
from app.models.entity import Entity
from app.models.narrative_cluster import NarrativeCluster
from app.models.alert import Alert
from app.models.case import Case
from app.models.edge import Edge
from app.models.watchlist import Watchlist, WatchlistEntry
from app.models.user import User

__all__ = [
    "Base",
    "ProvenanceMixin",
    "Source",
    "Actor",
    "Content",
    "MediaAsset",
    "Claim",
    "Entity",
    "NarrativeCluster",
    "Alert",
    "Case",
    "Edge",
    "Watchlist",
    "WatchlistEntry",
    "User",
]
