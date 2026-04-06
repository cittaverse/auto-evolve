#!/usr/bin/env python3
"""
REMem Memory Graph Builder

Implements episodic memory graph construction using NetworkX based on REMem (ICLR 2026).

Features:
- Graph-based memory storage (nodes=events, edges=relationships)
- Edge types: temporal, semantic, emotional, causal
- Memory strength tracking (for consolidation)
- Multi-hop retrieval support

Status: Phase 2 Implementation (Can run without LLM API using rule-based similarity)

References:
- REMem: Reasoning with Episodic Memory in Language Agent (ICLR 2026)
- Towards LLMs with Human-like Episodic Memory (Cell Press TiCS, 2025)
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
import networkx as nx
import logging

try:
    from .remem_event_segmenter import EventSegment
except ImportError:
    from remem_event_segmenter import EventSegment

logger = logging.getLogger(__name__)


@dataclass
class MemoryStrength:
    """Tracks memory strength with Ebbinghaus forgetting curve."""
    
    initial_strength: float = 1.0  # 0-1 scale
    current_strength: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)
    last_rehearsed: Optional[datetime] = None
    rehearsal_count: int = 0
    decay_rate: float = 0.1  # Per hour (adjustable)
    
    def decay(self, hours_elapsed: float) -> float:
        """Apply Ebbinghaus forgetting curve decay."""
        # Ebbinghaus: retention = e^(-t/s) where s is strength factor
        import math
        decay_factor = math.exp(-hours_elapsed * self.decay_rate)
        self.current_strength = self.initial_strength * decay_factor
        return self.current_strength
    
    def rehearse(self) -> None:
        """Boost memory strength through rehearsal."""
        self.rehearsal_count += 1
        self.last_rehearsed = datetime.now()
        # Rehearsal boosts initial strength (diminishing returns)
        boost = 0.2 * (0.5 ** (self.rehearsal_count - 1))  # 0.2, 0.1, 0.05, ...
        self.initial_strength = min(1.0, self.initial_strength + boost)
        self.current_strength = self.initial_strength
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'initial_strength': self.initial_strength,
            'current_strength': self.current_strength,
            'created_at': self.created_at.isoformat(),
            'last_rehearsed': self.last_rehearsed.isoformat() if self.last_rehearsed else None,
            'rehearsal_count': self.rehearsal_count,
            'decay_rate': self.decay_rate
        }


class EpisodicMemoryGraph:
    """
    Build and manage episodic memory graph from segmented events.
    
    Node Schema:
    - event_id: str
    - text: str
    - temporal_anchor: Optional[str]
    - emotional_valence: Optional[float]
    - people: List[str]
    - places: List[str]
    - themes: List[str]
    - memory_strength: MemoryStrength
    
    Edge Types:
    - TEMPORAL: before/after, same_period
    - SEMANTIC: similar_theme, same_people, same_place
    - EMOTIONAL: similar_valence, contrast
    - CAUSAL: led_to, triggered_by
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.event_index: Dict[str, str] = {}  # event_id -> node_id
        
    def add_event(self, event: EventSegment) -> str:
        """Add an event as a node in the graph."""
        node_id = f"event_{event.event_id}"
        
        memory_strength = MemoryStrength()
        
        self.graph.add_node(
            node_id,
            event_id=event.event_id,
            text=event.text,
            temporal_anchor=event.temporal_anchor,
            time_expression=event.time_expression,
            emotional_valence=event.emotional_valence,
            valence_label=event.valence_label,
            people=event.people_mentioned,
            places=event.places_mentioned,
            themes=event.themes,
            boundary_confidence=event.boundary_confidence,
            memory_strength=memory_strength,
            created_at=datetime.now()
        )
        
        self.event_index[event.event_id] = node_id
        logger.info(f"Added event node: {node_id} (anchor={event.temporal_anchor})")
        
        return node_id
    
    def build_from_segments(self, events: List[EventSegment]) -> List[str]:
        """Build graph from a list of segmented events."""
        node_ids = []
        for event in events:
            node_id = self.add_event(event)
            node_ids.append(node_id)
        
        # Build edges after all nodes are added
        self._build_temporal_edges(node_ids)
        self._build_semantic_edges(node_ids)
        self._build_emotional_edges(node_ids)
        
        logger.info(f"Built graph with {len(node_ids)} events, {self.graph.number_of_edges()} edges")
        return node_ids
    
    def _build_temporal_edges(self, node_ids: List[str]) -> int:
        """
        Build temporal edges based on event order and temporal anchors.
        
        Edge types:
        - NEXT: sequential order (event N -> event N+1)
        - BEFORE: explicit temporal ordering
        - SAME_PERIOD: share same temporal anchor (e.g., "大学期间")
        """
        edges_added = 0
        
        # Sequential NEXT edges
        for i in range(len(node_ids) - 1):
            self.graph.add_edge(node_ids[i], node_ids[i+1], relation='NEXT')
            edges_added += 1
        
        # Group by temporal anchor
        anchor_groups: Dict[str, List[str]] = {}
        for node_id in node_ids:
            anchor = self.graph.nodes[node_id].get('temporal_anchor')
            if anchor:
                if anchor not in anchor_groups:
                    anchor_groups[anchor] = []
                anchor_groups[anchor].append(node_id)
        
        # Add SAME_PERIOD edges within groups
        for anchor, nodes in anchor_groups.items():
            if len(nodes) > 1:
                for i in range(len(nodes)):
                    for j in range(i+1, len(nodes)):
                        self._add_edge_with_relations(nodes[i], nodes[j], 'SAME_PERIOD', anchor=anchor)
                        edges_added += 1
        
        logger.debug(f"Added {edges_added} temporal edges")
        return edges_added
    
    def _build_semantic_edges(self, node_ids: List[str]) -> int:
        """
        Build semantic edges based on shared people, places, and themes.
        
        Edge types:
        - SAME_PEOPLE: share people mentioned
        - SAME_PLACE: share places mentioned
        - SAME_THEME: share themes
        
        Note: Uses MultiDiGraph semantics by storing relations as a list on edges.
        """
        edges_added = 0
        
        # SAME_PEOPLE edges
        people_index: Dict[str, List[str]] = {}
        for node_id in node_ids:
            people = self.graph.nodes[node_id].get('people', [])
            for person in people:
                if person not in people_index:
                    people_index[person] = []
                people_index[person].append(node_id)
        
        for person, nodes in people_index.items():
            if len(nodes) > 1:
                for i in range(len(nodes)):
                    for j in range(i+1, len(nodes)):
                        self._add_edge_with_relations(nodes[i], nodes[j], 'SAME_PEOPLE', person=person)
                        edges_added += 1
        
        # SAME_PLACE edges
        place_index: Dict[str, List[str]] = {}
        for node_id in node_ids:
            places = self.graph.nodes[node_id].get('places', [])
            for place in places:
                if place not in place_index:
                    place_index[place] = []
                place_index[place].append(node_id)
        
        for place, nodes in place_index.items():
            if len(nodes) > 1:
                for i in range(len(nodes)):
                    for j in range(i+1, len(nodes)):
                        self._add_edge_with_relations(nodes[i], nodes[j], 'SAME_PLACE', place=place)
                        edges_added += 1
        
        # SAME_THEME edges
        theme_index: Dict[str, List[str]] = {}
        for node_id in node_ids:
            themes = self.graph.nodes[node_id].get('themes', [])
            for theme in themes:
                if theme not in theme_index:
                    theme_index[theme] = []
                theme_index[theme].append(node_id)
        
        for theme, nodes in theme_index.items():
            if len(nodes) > 1:
                for i in range(len(nodes)):
                    for j in range(i+1, len(nodes)):
                        self._add_edge_with_relations(nodes[i], nodes[j], 'SAME_THEME', theme=theme)
                        edges_added += 1
        
        logger.debug(f"Added {edges_added} semantic edges")
        return edges_added
    
    def _add_edge_with_relations(self, source: str, target: str, relation: str, **attrs):
        """Add edge or update existing edge with additional relations."""
        if self.graph.has_edge(source, target):
            # Edge exists, get current data
            edge_data = dict(self.graph.get_edge_data(source, target))
            
            # Initialize relations list if not present
            if 'relations' not in edge_data:
                edge_data['relations'] = [edge_data.get('relation')]
            
            # Add new relation if not already present
            if relation not in edge_data['relations']:
                edge_data['relations'].append(relation)
            
            # Merge new attributes
            for k, v in attrs.items():
                # If attribute already exists and is different, keep both in a list
                if k in edge_data and edge_data[k] != v:
                    existing = edge_data[k]
                    if isinstance(existing, list):
                        if v not in existing:
                            existing.append(v)
                    else:
                        edge_data[k] = [existing, v]
                else:
                    edge_data[k] = v
            
            # Update the primary relation to show all
            edge_data['relation'] = ', '.join(edge_data['relations'])
            
            # Remove and re-add to update
            self.graph.remove_edge(source, target)
            self.graph.add_edge(source, target, **edge_data)
        else:
            # New edge with relations as a list
            self.graph.add_edge(source, target, relation=relation, relations=[relation], **attrs)
    
    def _build_emotional_edges(self, node_ids: List[str]) -> int:
        """
        Build emotional edges based on valence similarity or contrast.
        
        Edge types:
        - SIMILAR_VALENCE: both positive or both negative (within 15 points)
        - CONTRAST: one positive, one negative (difference > 40 points)
        """
        edges_added = 0
        
        for i in range(len(node_ids)):
            for j in range(i+1, len(node_ids)):
                valence_i = self.graph.nodes[node_ids[i]].get('emotional_valence')
                valence_j = self.graph.nodes[node_ids[j]].get('emotional_valence')
                
                if valence_i is None or valence_j is None:
                    continue
                
                diff = abs(valence_i - valence_j)
                
                if diff <= 15:
                    # Similar valence
                    self._add_edge_with_relations(node_ids[i], node_ids[j], 'SIMILAR_VALENCE', diff=diff)
                    edges_added += 1
                elif diff > 40:
                    # Emotional contrast
                    self._add_edge_with_relations(node_ids[i], node_ids[j], 'CONTRAST', diff=diff)
                    edges_added += 1
        
        logger.debug(f"Added {edges_added} emotional edges")
        return edges_added
    
    def get_node(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get node data by event_id."""
        node_id = self.event_index.get(event_id)
        if node_id and self.graph.has_node(node_id):
            return dict(self.graph.nodes[node_id])
        return None
    
    def get_neighbors(self, event_id: str, relation: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get neighboring events connected by edges.
        
        Args:
            event_id: Source event ID
            relation: Filter by edge relation type (optional). Checks the 'relations' list.
        
        Returns:
            List of neighbor node data with edge info
        """
        node_id = self.event_index.get(event_id)
        if not node_id or not self.graph.has_node(node_id):
            return []
        
        neighbors = []
        
        # Get successors and predecessors
        for neighbor_id in list(self.graph.successors(node_id)) + list(self.graph.predecessors(node_id)):
            edge_data = self.graph.get_edge_data(node_id, neighbor_id)
            if edge_data:
                # Check relations list (or fall back to single relation)
                edge_relations = edge_data.get('relations', [edge_data.get('relation')])
                if relation is None or relation in edge_relations:
                    neighbor_data = dict(self.graph.nodes[neighbor_id])
                    neighbor_data['_edge'] = edge_data
                    neighbors.append(neighbor_data)
        
        return neighbors
    
    def query_by_temporal_anchor(self, anchor: str) -> List[Dict[str, Any]]:
        """Get all events with a specific temporal anchor."""
        results = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get('temporal_anchor') == anchor:
                results.append(dict(data))
        return results
    
    def query_by_theme(self, theme: str) -> List[Dict[str, Any]]:
        """Get all events containing a specific theme."""
        results = []
        for node_id, data in self.graph.nodes(data=True):
            themes = data.get('themes', [])
            if theme in themes:
                results.append(dict(data))
        return results
    
    def multi_hop_traversal(
        self,
        start_event_id: str,
        max_hops: int = 2,
        relations: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform multi-hop graph traversal from a starting event.
        
        Args:
            start_event_id: Starting event ID
            max_hops: Maximum number of hops (default 2)
            relations: Allowed edge relations (None = all)
        
        Returns:
            List of reachable events with path information
        """
        start_node = self.event_index.get(start_event_id)
        if not start_node:
            return []
        
        visited = {start_node}
        queue = [(start_node, 0, [start_node])]  # (node, hops, path)
        results = []
        
        while queue:
            current, hops, path = queue.pop(0)
            
            if hops >= max_hops:
                continue
            
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited:
                    edge_data = self.graph.get_edge_data(current, neighbor)
                    relation = edge_data.get('relation')
                    
                    if relations is None or relation in relations:
                        visited.add(neighbor)
                        new_path = path + [neighbor]
                        
                        neighbor_data = dict(self.graph.nodes[neighbor])
                        neighbor_data['_path'] = new_path
                        neighbor_data['_hops'] = hops + 1
                        results.append(neighbor_data)
                        
                        queue.append((neighbor, hops + 1, new_path))
        
        return results
    
    def apply_consolidation(self, hours_elapsed: float = 1.0) -> Dict[str, Any]:
        """
        Apply memory consolidation across all events.
        
        Args:
            hours_elapsed: Hours since last consolidation
        
        Returns:
            Summary of consolidation effects
        """
        strengthened = 0
        decayed = 0
        pruned = 0
        
        # First pass: apply decay and collect nodes to prune
        nodes_to_prune = []
        
        for node_id in list(self.graph.nodes()):  # Use list() to avoid modification during iteration
            strength: MemoryStrength = self.graph.nodes[node_id].get('memory_strength')
            if strength:
                old_strength = strength.current_strength
                
                # Apply decay
                strength.decay(hours_elapsed)
                
                # Boost if rehearsed recently
                if strength.last_rehearsed:
                    hours_since_rehearsal = (datetime.now() - strength.last_rehearsed).total_seconds() / 3600
                    if hours_since_rehearsal < hours_elapsed:
                        strength.rehearse()
                        strengthened += 1
                
                if strength.current_strength < old_strength:
                    decayed += 1
                
                # Collect very weak memories for pruning
                if strength.current_strength < 0.1:
                    nodes_to_prune.append(node_id)
        
        # Second pass: remove weak nodes
        for node_id in nodes_to_prune:
            if self.graph.has_node(node_id):
                event_id = self.graph.nodes[node_id].get('event_id')
                self.graph.remove_node(node_id)
                pruned += 1
                # Update index
                if event_id and event_id in self.event_index:
                    del self.event_index[event_id]
        
        return {
            'strengthened': strengthened,
            'decayed': decayed,
            'pruned': pruned,
            'remaining_nodes': len(self.graph.nodes())
        }
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            'num_events': len(self.graph.nodes()),
            'num_edges': len(self.graph.edges()),
            'avg_degree': sum(dict(self.graph.degree()).values()) / len(self.graph.nodes()) if self.graph.nodes() else 0,
            'num_connected_components': nx.number_weakly_connected_components(self.graph) if self.graph.nodes() else 0,
            'edge_relations': self._count_edge_relations()
        }
    
    def _count_edge_relations(self) -> Dict[str, int]:
        """Count edges by relation type."""
        counts: Dict[str, int] = {}
        for _, _, data in self.graph.edges(data=True):
            relation = data.get('relation', 'UNKNOWN')
            counts[relation] = counts.get(relation, 0) + 1
        return counts
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary."""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            node_copy = dict(data)
            if 'memory_strength' in node_copy:
                node_copy['memory_strength'] = node_copy['memory_strength'].to_dict()
            nodes.append(node_copy)
        
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                'source': u,
                'target': v,
                'relation': data.get('relation'),
                **{k: v for k, v in data.items() if k != 'relation'}
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': self.get_graph_stats()
        }


# Example usage and test
if __name__ == '__main__':
    # Test with mock events
    from remem_event_segmenter import EventSegment
    
    mock_events = [
        EventSegment(
            event_id='e1',
            text='2010 年大学毕业后，我来到了北京工作。那时候刚毕业，充满激情。',
            start_pos=0,
            end_pos=30,
            temporal_anchor='2010 年',
            emotional_valence=75.0,
            valence_label='positive',
            people=['我'],
            places=['北京'],
            themes=['工作', '毕业']
        ),
        EventSegment(
            event_id='e2',
            text='2012 年遇到了我的妻子，我们是在一次朋友聚会上认识的。',
            start_pos=31,
            end_pos=60,
            temporal_anchor='2012 年',
            emotional_valence=85.0,
            valence_label='positive',
            people=['我', '妻子'],
            places=[],
            themes=['爱情', '婚姻']
        ),
        EventSegment(
            event_id='e3',
            text='2015 年我们结婚了，那时候生活虽然简单但很幸福。',
            start_pos=61,
            end_pos=90,
            temporal_anchor='2015 年',
            emotional_valence=90.0,
            valence_label='positive',
            people=['我', '妻子'],
            places=[],
            themes=['婚姻', '幸福']
        )
    ]
    
    graph = EpisodicMemoryGraph()
    graph.build_from_segments(mock_events)
    
    print("Graph Statistics:")
    stats = graph.get_graph_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nMulti-hop traversal from e1:")
    results = graph.multi_hop_traversal('e1', max_hops=2)
    for result in results:
        print(f"  {result['event_id']}: {result.get('temporal_anchor')} ({result.get('_hops')} hops)")
    
    print("\nConsolidation after 24 hours:")
    consolidation = graph.apply_consolidation(hours_elapsed=24.0)
    print(f"  {consolidation}")
