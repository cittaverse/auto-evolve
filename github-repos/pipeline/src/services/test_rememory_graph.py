#!/usr/bin/env python3
"""
Test suite for REMem Memory Graph Builder

Tests:
- Graph construction from segments
- Edge building (temporal, semantic, emotional)
- Multi-hop traversal
- Memory consolidation
- Query operations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Use absolute imports for standalone test
from remem_memory_graph import EpisodicMemoryGraph, MemoryStrength
from remem_event_segmenter import EventSegment as EventSegmentLocal
from datetime import datetime, timedelta

# Alias for compatibility
EventSegment = EventSegmentLocal


def test_graph_construction():
    """Test basic graph construction from event segments."""
    print("Test 1: Graph Construction")
    
    events = [
        EventSegment(
            event_id='e1',
            text='2010 年大学毕业后，我来到了北京工作。',
            start_pos=0,
            end_pos=20,
            temporal_anchor='2010 年',
            emotional_valence=75.0,
            valence_label='positive',
            people_mentioned=['我'],
            places_mentioned=['北京'],
            themes=['工作', '毕业'],
            boundary_confidence=0.8
        ),
        EventSegment(
            event_id='e2',
            text='2012 年遇到了我的妻子。',
            start_pos=21,
            end_pos=35,
            temporal_anchor='2012 年',
            emotional_valence=85.0,
            valence_label='positive',
            people_mentioned=['我', '妻子'],
            places_mentioned=[],
            themes=['爱情', '婚姻'],
            boundary_confidence=0.9
        ),
        EventSegment(
            event_id='e3',
            text='2015 年我们结婚了。',
            start_pos=36,
            end_pos=50,
            temporal_anchor='2015 年',
            emotional_valence=90.0,
            valence_label='positive',
            people_mentioned=['我', '妻子'],
            places_mentioned=[],
            themes=['婚姻', '幸福'],
            boundary_confidence=0.85
        )
    ]
    
    graph = EpisodicMemoryGraph()
    node_ids = graph.build_from_segments(events)
    
    assert len(node_ids) == 3, f"Expected 3 nodes, got {len(node_ids)}"
    assert graph.graph.number_of_nodes() == 3, f"Expected 3 nodes in graph"
    
    stats = graph.get_graph_stats()
    print(f"  ✓ Created graph with {stats['num_events']} events, {stats['num_edges']} edges")
    print(f"  ✓ Edge relations: {stats['edge_relations']}")
    print()


def test_temporal_edges():
    """Test temporal edge construction."""
    print("Test 2: Temporal Edges")
    
    events = [
        EventSegment(
            event_id='e1',
            text='大学期间...',
            start_pos=0,
            end_pos=10,
            temporal_anchor='大学期间',
            emotional_valence=70.0,
            people_mentioned=[],
            places_mentioned=[],
            themes=[]
        ),
        EventSegment(
            event_id='e2',
            text='大学期间另一件事...',
            start_pos=11,
            end_pos=25,
            temporal_anchor='大学期间',
            emotional_valence=65.0,
            people_mentioned=[],
            places_mentioned=[],
            themes=[]
        ),
        EventSegment(
            event_id='e3',
            text='工作后...',
            start_pos=26,
            end_pos=35,
            temporal_anchor='工作后',
            emotional_valence=80.0,
            people_mentioned=[],
            places_mentioned=[],
            themes=[]
        )
    ]
    
    graph = EpisodicMemoryGraph()
    graph.build_from_segments(events)
    
    # Check NEXT edges (directed: e1 -> e2)
    # Edges can have multiple relations stored in 'relations' list
    e1_successors = list(graph.graph.successors(graph.event_index['e1']))
    has_next = False
    for s in e1_successors:
        edge_data = graph.graph.get_edge_data('event_e1', s)
        relations = edge_data.get('relations', [edge_data.get('relation')])
        if 'NEXT' in relations:
            has_next = True
            break
    
    assert has_next, "Expected NEXT edge from e1 to e2"
    
    # Check SAME_PERIOD edges
    e1_same_period = graph.get_neighbors('e1', relation='SAME_PERIOD')
    assert len(e1_same_period) >= 1, "Expected SAME_PERIOD edge between e1 and e2"
    
    print(f"  ✓ NEXT edges: sequential ordering correct")
    print(f"  ✓ SAME_PERIOD edges: grouped by temporal anchor")
    print()


def test_semantic_edges():
    """Test semantic edge construction."""
    print("Test 3: Semantic Edges")
    
    events = [
        EventSegment(
            event_id='e1',
            text='和妻子一起去北京旅行',
            start_pos=0,
            end_pos=15,
            people_mentioned=['我', '妻子'],
            places_mentioned=['北京'],
            themes=['旅行', '爱情'],
            emotional_valence=None
        ),
        EventSegment(
            event_id='e2',
            text='妻子在上海工作',
            start_pos=16,
            end_pos=25,
            people_mentioned=['妻子'],
            places_mentioned=['上海'],
            themes=['工作'],
            emotional_valence=None
        ),
        EventSegment(
            event_id='e3',
            text='我在北京工作',
            start_pos=26,
            end_pos=35,
            people_mentioned=['我'],
            places_mentioned=['北京'],
            themes=['工作'],
            emotional_valence=None
        )
    ]
    
    graph = EpisodicMemoryGraph()
    graph.build_from_segments(events)
    
    # Check SAME_PEOPLE (e1 and e2 share '妻子')
    e1_people = graph.get_neighbors('e1', relation='SAME_PEOPLE')
    assert len(e1_people) >= 1, "Expected SAME_PEOPLE edge"
    
    # Check SAME_PLACE (e1 and e3 share '北京')
    e1_place = graph.get_neighbors('e1', relation='SAME_PLACE')
    assert len(e1_place) >= 1, "Expected SAME_PLACE edge"
    
    # Check SAME_THEME (e2 and e3 share '工作')
    e2_theme = graph.get_neighbors('e2', relation='SAME_THEME')
    assert len(e2_theme) >= 1, "Expected SAME_THEME edge"
    
    print(f"  ✓ SAME_PEOPLE edges: connected by shared people")
    print(f"  ✓ SAME_PLACE edges: connected by shared places")
    print(f"  ✓ SAME_THEME edges: connected by shared themes")
    print()


def test_emotional_edges():
    """Test emotional edge construction."""
    print("Test 4: Emotional Edges")
    
    events = [
        EventSegment(
            event_id='e1',
            text='非常开心的事',
            start_pos=0,
            end_pos=10,
            emotional_valence=90.0,
            people_mentioned=[],
            places_mentioned=[],
            themes=[]
        ),
        EventSegment(
            event_id='e2',
            text='也比较开心',
            start_pos=11,
            end_pos=20,
            emotional_valence=80.0,
            people_mentioned=[],
            places_mentioned=[],
            themes=[]
        ),
        EventSegment(
            event_id='e3',
            text='非常难过的事',
            start_pos=21,
            end_pos=30,
            emotional_valence=20.0,
            people_mentioned=[],
            places_mentioned=[],
            themes=[]
        )
    ]
    
    graph = EpisodicMemoryGraph()
    graph.build_from_segments(events)
    
    # Check SIMILAR_VALENCE (e1 and e2: diff=10)
    e1_similar = graph.get_neighbors('e1', relation='SIMILAR_VALENCE')
    assert len(e1_similar) >= 1, "Expected SIMILAR_VALENCE edge between e1 and e2"
    
    # Check CONTRAST (e1 and e3: diff=70)
    e1_contrast = graph.get_neighbors('e1', relation='CONTRAST')
    assert len(e1_contrast) >= 1, "Expected CONTRAST edge between e1 and e3"
    
    print(f"  ✓ SIMILAR_VALENCE edges: connected by similar emotions")
    print(f"  ✓ CONTRAST edges: connected by emotional contrast")
    print()


def test_multi_hop_traversal():
    """Test multi-hop graph traversal."""
    print("Test 5: Multi-hop Traversal")
    
    events = [
        EventSegment(
            event_id='e1',
            text='起点事件',
            start_pos=0,
            end_pos=10,
            people_mentioned=['我'],
            themes=['起点'],
            emotional_valence=None
        ),
        EventSegment(
            event_id='e2',
            text='中间事件 1',
            start_pos=11,
            end_pos=20,
            people_mentioned=['我'],
            themes=['中间'],
            emotional_valence=None
        ),
        EventSegment(
            event_id='e3',
            text='中间事件 2',
            start_pos=21,
            end_pos=30,
            people_mentioned=['我'],
            themes=['中间'],
            emotional_valence=None
        ),
        EventSegment(
            event_id='e4',
            text='终点事件',
            start_pos=31,
            end_pos=40,
            people_mentioned=['我'],
            themes=['终点'],
            emotional_valence=None
        )
    ]
    
    graph = EpisodicMemoryGraph()
    graph.build_from_segments(events)
    
    # 1-hop from e1
    results_1hop = graph.multi_hop_traversal('e1', max_hops=1)
    assert len(results_1hop) >= 1, "Expected at least 1 result at 1 hop"
    
    # 2-hop from e1
    results_2hop = graph.multi_hop_traversal('e1', max_hops=2)
    assert len(results_2hop) >= 2, "Expected at least 2 results at 2 hops"
    
    print(f"  ✓ 1-hop: {len(results_1hop)} reachable events")
    print(f"  ✓ 2-hop: {len(results_2hop)} reachable events")
    print()


def test_memory_consolidation():
    """Test memory strength decay and rehearsal."""
    print("Test 6: Memory Consolidation")
    
    events = [
        EventSegment(
            event_id='e1',
            text='重要事件',
            start_pos=0,
            end_pos=10,
            emotional_valence=90.0,
            people_mentioned=[],
            places_mentioned=[],
            themes=[]
        )
    ]
    
    graph = EpisodicMemoryGraph()
    graph.build_from_segments(events)
    
    # Get initial strength
    node_data = graph.get_node('e1')
    initial_strength = node_data['memory_strength'].current_strength
    assert initial_strength == 1.0, "Expected initial strength = 1.0"
    
    # Apply 1 hour of decay (not 24h, which would prune the node)
    consolidation = graph.apply_consolidation(hours_elapsed=1.0)
    
    node_data = graph.get_node('e1')
    decayed_strength = node_data['memory_strength'].current_strength
    assert decayed_strength < initial_strength, "Expected strength to decay"
    assert decayed_strength > 0.1, "Expected node to not be pruned"
    
    print(f"  ✓ Initial strength: {initial_strength:.3f}")
    print(f"  ✓ After 1h decay: {decayed_strength:.3f}")
    print(f"  ✓ Consolidation summary: {consolidation}")
    print()


def test_query_operations():
    """Test query operations."""
    print("Test 7: Query Operations")
    
    events = [
        EventSegment(
            event_id='e1',
            text='2010 年北京工作',
            start_pos=0,
            end_pos=10,
            temporal_anchor='2010 年',
            places_mentioned=['北京'],
            themes=['工作'],
            emotional_valence=None
        ),
        EventSegment(
            event_id='e2',
            text='2010 年上海旅行',
            start_pos=11,
            end_pos=20,
            temporal_anchor='2010 年',
            places_mentioned=['上海'],
            themes=['旅行'],
            emotional_valence=None
        ),
        EventSegment(
            event_id='e3',
            text='2015 年北京工作',
            start_pos=21,
            end_pos=30,
            temporal_anchor='2015 年',
            places_mentioned=['北京'],
            themes=['工作'],
            emotional_valence=None
        )
    ]
    
    graph = EpisodicMemoryGraph()
    graph.build_from_segments(events)
    
    # Query by temporal anchor
    results_2010 = graph.query_by_temporal_anchor('2010 年')
    assert len(results_2010) == 2, "Expected 2 events in 2010 年"
    
    # Query by theme
    results_work = graph.query_by_theme('工作')
    assert len(results_work) == 2, "Expected 2 events with theme 工作"
    
    print(f"  ✓ Query by temporal anchor '2010 年': {len(results_2010)} events")
    print(f"  ✓ Query by theme '工作': {len(results_work)} events")
    print()


def test_serialization():
    """Test graph serialization."""
    print("Test 8: Serialization")
    
    events = [
        EventSegment(
            event_id='e1',
            text='测试事件',
            start_pos=0,
            end_pos=10,
            temporal_anchor='2020 年',
            emotional_valence=75.0,
            people_mentioned=[],
            places_mentioned=[],
            themes=[]
        )
    ]
    
    graph = EpisodicMemoryGraph()
    graph.build_from_segments(events)
    
    graph_dict = graph.to_dict()
    
    assert 'nodes' in graph_dict, "Expected 'nodes' in serialized graph"
    assert 'edges' in graph_dict, "Expected 'edges' in serialized graph"
    assert 'stats' in graph_dict, "Expected 'stats' in serialized graph"
    assert len(graph_dict['nodes']) == 1, "Expected 1 node in serialized graph"
    
    print(f"  ✓ Serialized graph: {len(graph_dict['nodes'])} nodes, {len(graph_dict['edges'])} edges")
    print(f"  ✓ Stats included: {list(graph_dict['stats'].keys())}")
    print()


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("REMem Memory Graph Builder - Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_graph_construction()
        test_temporal_edges()
        test_semantic_edges()
        test_emotional_edges()
        test_multi_hop_traversal()
        test_memory_consolidation()
        test_query_operations()
        test_serialization()
        
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
