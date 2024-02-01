def slice_scores(scores: dict, slice_index: int, slice_count: int):
    """Take a specific slice from the given scores"""
    assert slice_index >= 0
    assert slice_index < slice_count
    
    score_ids = list(scores.keys())
    slice_size = len(score_ids) // slice_count
    
    slice_score_ids = score_ids[
        (slice_index * slice_size) : ((slice_index + 1) * slice_size)
    ]
    if slice_index == slice_count - 1:
        slice_score_ids = score_ids[(slice_index * slice_size):]
    
    return {
        score_id: score
        for score_id, score in scores.items()
        if score_id in set(slice_score_ids)
    }