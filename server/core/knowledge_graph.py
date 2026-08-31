import time
import uuid
import math
from typing import Dict, Any, List, Optional, Set
from server.core.models import KnowledgeEntity, KnowledgeRelation

class KnowledgeGraphEngine:
    """
    JARVIS-V2 4-Tier Cognitive Knowledge Graph Engine.
    Combines:
    1. Working Memory Buffer (active context tokens)
    2. Episodic Log (action and decision history)
    3. Semantic Knowledge Graph (entities and relation triples)
    4. Procedural Playbooks (automated multi-agent workflows)
    """

    def __init__(self):
        self.entities: Dict[str, KnowledgeEntity] = {}
        self.relations: List[KnowledgeRelation] = []
        self.playbooks: Dict[str, Dict[str, Any]] = {}
        self.working_memory: Dict[str, Any] = {}
        self._seed_default_knowledge()

    def _seed_default_knowledge(self):
        """Seeds initial system entities and foundational knowledge"""
        self.add_entity(
            name="JARVIS Core",
            entity_type="system",
            properties={"version": "V2.0", "engine": "FastAPI/React", "status": "operational"}
        )
        self.add_entity(
            name="Suyash Pandey",
            entity_type="person",
            properties={"role": "Chief Operator / Lead Architect", "permissions": "Admin"}
        )
        self.add_relation("JARVIS Core", "Suyash Pandey", "ASSISTS", weight=1.0)

        # Seed standard procedural playbooks
        self.register_playbook(
            playbook_id="incident_triage_routine",
            name="Full Security Triage & Isolation Playbook",
            description="Executes Tier 1 triage, blast radius calculation, and containment proposal.",
            steps=[
                {"agent": "tier1_triage", "action": "normalize_and_score"},
                {"agent": "tier2_responder", "action": "blast_radius_investigation"},
                {"agent": "threat_intel", "action": "ioc_lookup"}
            ]
        )
        self.register_playbook(
            playbook_id="system_health_audit",
            name="Host Telemetry & Vulnerability Sweep",
            description="Scans CPU load, storage, live ports, and running process lineage.",
            steps=[
                {"agent": "system_agent", "action": "get_system_vitals"},
                {"agent": "endpoint_security", "action": "inspect_process_tree"},
                {"agent": "network_security", "action": "scan_active_sockets"}
            ]
        )

    def add_entity(self, name: str, entity_type: str, properties: Optional[Dict[str, Any]] = None) -> KnowledgeEntity:
        entity_id = f"ent_{name.lower().replace(' ', '_')}"
        if entity_id in self.entities:
            self.entities[entity_id].properties.update(properties or {})
            self.entities[entity_id].updated_at = time.time()
            return self.entities[entity_id]

        entity = KnowledgeEntity(
            entity_id=entity_id,
            name=name,
            entity_type=entity_type,
            properties=properties or {}
        )
        self.entities[entity_id] = entity
        return entity

    def add_relation(
        self,
        source_name_or_id: str,
        target_name_or_id: str,
        relation_type: str,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> KnowledgeRelation:
        src_id = source_name_or_id if source_name_or_id.startswith("ent_") else f"ent_{source_name_or_id.lower().replace(' ', '_')}"
        tgt_id = target_name_or_id if target_name_or_id.startswith("ent_") else f"ent_{target_name_or_id.lower().replace(' ', '_')}"

        rel = KnowledgeRelation(
            relation_id=f"rel_{uuid.uuid4().hex[:8]}",
            source_id=src_id,
            target_id=tgt_id,
            relation_type=relation_type,
            weight=weight,
            metadata=metadata or {}
        )
        self.relations.append(rel)
        return rel

    def get_related_entities(self, entity_name_or_id: str) -> List[Dict[str, Any]]:
        target_id = entity_name_or_id if entity_name_or_id.startswith("ent_") else f"ent_{entity_name_or_id.lower().replace(' ', '_')}"
        results = []

        for rel in self.relations:
            if rel.source_id == target_id and rel.target_id in self.entities:
                results.append({
                    "relationship": rel.relation_type,
                    "direction": "outgoing",
                    "entity": self.entities[rel.target_id].dict()
                })
            elif rel.target_id == target_id and rel.source_id in self.entities:
                results.append({
                    "relationship": rel.relation_type,
                    "direction": "incoming",
                    "entity": self.entities[rel.source_id].dict()
                })

        return results

    def search_knowledge_hybrid(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Hybrid search across entities and property values using token overlap scoring.
        """
        q_tokens = set(query.lower().split())
        scored_entities = []

        for eid, ent in self.entities.items():
            ent_tokens = set(ent.name.lower().split()) | set(ent.entity_type.lower().split())
            for val in ent.properties.values():
                ent_tokens |= set(str(val).lower().split())

            overlap = len(q_tokens & ent_tokens)
            if overlap > 0:
                scored_entities.append((overlap, ent))

        scored_entities.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "score": score,
                "entity": ent.dict(),
                "related": self.get_related_entities(ent.entity_id)
            }
            for score, ent in scored_entities[:limit]
        ]

    def register_playbook(self, playbook_id: str, name: str, description: str, steps: List[Dict[str, Any]]):
        self.playbooks[playbook_id] = {
            "playbook_id": playbook_id,
            "name": name,
            "description": description,
            "steps": steps,
            "created_at": time.time()
        }

    def get_playbook(self, playbook_id: str) -> Optional[Dict[str, Any]]:
        return self.playbooks.get(playbook_id)

    def set_working_context(self, key: str, value: Any):
        self.working_memory[key] = value

    def get_working_context(self, key: str, default: Any = None) -> Any:
        return self.working_memory.get(key, default)

knowledge_graph = KnowledgeGraphEngine()
