"""
Knowledge Graph Module

Graph-based knowledge representation for nano-fertilizer LCA-TEA.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
import json


class EntityType(Enum):
    """Types of entities in the knowledge graph."""
    MATERIAL = "material"
    PROCESS = "process"
    PRODUCT = "product"
    EMISSION = "emission"
    IMPACT = "impact"
    TECHNOLOGY = "technology"
    COUNTRY = "country"
    REGULATION = "regulation"
    PARAMETER = "parameter"


class RelationType(Enum):
    """Types of relationships in the knowledge graph."""
    REQUIRES = "requires"
    PRODUCES = "produces"
    EMITS = "emits"
    IMPACTS = "impacts"
    LOCATED_IN = "located_in"
    REGULATES = "regulates"
    ALTERNATIVE_TO = "alternative_to"
    DERIVED_FROM = "derived_from"
    PART_OF = "part_of"


@dataclass
class Entity:
    """A node in the knowledge graph."""
    
    id: str
    name: str
    entity_type: EntityType
    properties: Dict = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.entity_type.value,
            "properties": self.properties,
            "sources": self.sources
        }


@dataclass
class Relationship:
    """An edge in the knowledge graph."""
    
    source_id: str
    target_id: str
    relation_type: RelationType
    properties: Dict = field(default_factory=dict)
    weight: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.relation_type.value,
            "properties": self.properties,
            "weight": self.weight
        }


class KnowledgeGraph:
    """
    Knowledge Graph for nano-fertilizer LCA-TEA domain.
    
    Stores entities and relationships as a graph structure.
    Uses NetworkX for graph operations when available.
    """
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self._graph = None
        
        # Try to use NetworkX
        try:
            import networkx as nx
            self._graph = nx.DiGraph()
            self._use_networkx = True
        except ImportError:
            self._use_networkx = False
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the graph."""
        self.entities[entity.id] = entity
        
        if self._use_networkx:
            self._graph.add_node(
                entity.id,
                name=entity.name,
                type=entity.entity_type.value,
                **entity.properties
            )
    
    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship to the graph."""
        self.relationships.append(relationship)
        
        if self._use_networkx:
            self._graph.add_edge(
                relationship.source_id,
                relationship.target_id,
                type=relationship.relation_type.value,
                weight=relationship.weight,
                **relationship.properties
            )
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self.entities.get(entity_id)
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """Get all entities of a specific type."""
        return [e for e in self.entities.values() if e.entity_type == entity_type]
    
    def get_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relation_type: Optional[RelationType] = None
    ) -> List[Relationship]:
        """Query relationships with optional filters."""
        results = self.relationships
        
        if source_id:
            results = [r for r in results if r.source_id == source_id]
        if target_id:
            results = [r for r in results if r.target_id == target_id]
        if relation_type:
            results = [r for r in results if r.relation_type == relation_type]
        
        return results
    
    def get_neighbors(self, entity_id: str) -> List[Entity]:
        """Get neighboring entities."""
        if self._use_networkx:
            neighbor_ids = list(self._graph.neighbors(entity_id))
            return [self.entities[nid] for nid in neighbor_ids if nid in self.entities]
        else:
            neighbor_ids = set()
            for r in self.relationships:
                if r.source_id == entity_id:
                    neighbor_ids.add(r.target_id)
            return [self.entities[nid] for nid in neighbor_ids if nid in self.entities]
    
    def find_path(
        self,
        source_id: str,
        target_id: str
    ) -> Optional[List[str]]:
        """Find path between two entities."""
        if self._use_networkx:
            import networkx as nx
            try:
                return nx.shortest_path(self._graph, source_id, target_id)
            except nx.NetworkXNoPath:
                return None
        return None
    
    def to_dict(self) -> Dict:
        """Export graph as dictionary."""
        return {
            "entities": [e.to_dict() for e in self.entities.values()],
            "relationships": [r.to_dict() for r in self.relationships],
            "stats": {
                "entity_count": len(self.entities),
                "relationship_count": len(self.relationships)
            }
        }
    
    def to_json(self, filepath: str) -> None:
        """Export graph to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def from_json(self, filepath: str) -> None:
        """Load graph from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        
        for e_data in data.get("entities", []):
            entity = Entity(
                id=e_data["id"],
                name=e_data["name"],
                entity_type=EntityType(e_data["type"]),
                properties=e_data.get("properties", {}),
                sources=e_data.get("sources", [])
            )
            self.add_entity(entity)
        
        for r_data in data.get("relationships", []):
            rel = Relationship(
                source_id=r_data["source"],
                target_id=r_data["target"],
                relation_type=RelationType(r_data["type"]),
                properties=r_data.get("properties", {}),
                weight=r_data.get("weight", 1.0)
            )
            self.add_relationship(rel)


def create_nanop_base_graph() -> KnowledgeGraph:
    """
    Create base knowledge graph for nano-P fertilizer domain.
    """
    kg = KnowledgeGraph()
    
    # Materials
    materials = [
        ("mat_cacl2", "Calcium Chloride (CaCl2)", {"formula": "CaCl2", "mw": 110.98}),
        ("mat_h3po4", "Phosphoric Acid (H3PO4)", {"formula": "H3PO4", "mw": 97.99}),
        ("mat_nh4oh", "Ammonium Hydroxide (NH4OH)", {"formula": "NH4OH", "mw": 35.05}),
        ("mat_water", "Deionized Water", {"formula": "H2O", "mw": 18.02}),
    ]
    
    for mid, name, props in materials:
        kg.add_entity(Entity(
            id=mid, name=name,
            entity_type=EntityType.MATERIAL,
            properties=props
        ))
    
    # Products
    products = [
        ("prod_nanop", "Nano Hydroxyapatite (NanoP)", {"formula": "Ca10(PO4)6(OH)2", "mw": 1004.6}),
        ("prod_nh4cl", "Ammonium Chloride (NH4Cl)", {"formula": "NH4Cl", "mw": 53.49}),
    ]
    
    for pid, name, props in products:
        kg.add_entity(Entity(
            id=pid, name=name,
            entity_type=EntityType.PRODUCT,
            properties=props
        ))
    
    # Process
    kg.add_entity(Entity(
        id="proc_synthesis",
        name="Wet Chemical Precipitation",
        entity_type=EntityType.PROCESS,
        properties={"temperature": 80, "ph": 10, "trl": 7}
    ))
    
    # Emissions
    emissions = [
        ("emit_co2", "CO2", {"impact": "climate_change"}),
        ("emit_nh3", "NH3", {"impact": "acidification"}),
        ("emit_nox", "NOx", {"impact": "acidification"}),
    ]
    
    for eid, name, props in emissions:
        kg.add_entity(Entity(
            id=eid, name=name,
            entity_type=EntityType.EMISSION,
            properties=props
        ))
    
    # Relationships: Materials -> Process
    for mid, _, _ in materials:
        kg.add_relationship(Relationship(
            source_id="proc_synthesis",
            target_id=mid,
            relation_type=RelationType.REQUIRES
        ))
    
    # Relationships: Process -> Products
    for pid, _, _ in products:
        kg.add_relationship(Relationship(
            source_id="proc_synthesis",
            target_id=pid,
            relation_type=RelationType.PRODUCES
        ))
    
    # Relationships: Process -> Emissions
    for eid, _, _ in emissions:
        kg.add_relationship(Relationship(
            source_id="proc_synthesis",
            target_id=eid,
            relation_type=RelationType.EMITS
        ))
    
    return kg


if __name__ == "__main__":
    kg = create_nanop_base_graph()
    print(f"Knowledge Graph created:")
    print(f"  Entities: {len(kg.entities)}")
    print(f"  Relationships: {len(kg.relationships)}")
    
    # Example query
    process = kg.get_entity("proc_synthesis")
    print(f"\nProcess: {process.name}")
    print(f"  Neighbors: {[e.name for e in kg.get_neighbors('proc_synthesis')]}")
