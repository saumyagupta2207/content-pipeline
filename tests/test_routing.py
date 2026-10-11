from pipeline.nodes import MAX_LOOPS, PASS_SCORE, should_revise


def make_state(score, loops):
    return {"score": score, "loops": loops}


def test_publishes_when_score_passes():
    assert should_revise(make_state(PASS_SCORE, 1)) == "publish"


def test_revises_when_score_low_and_loops_left():
    assert should_revise(make_state(PASS_SCORE - 1, 1)) == "revise"


def test_publishes_when_out_of_loops_even_if_score_low():
    assert should_revise(make_state(2, MAX_LOOPS)) == "publish"


def test_high_score_on_last_loop_still_publishes():
    assert should_revise(make_state(9, MAX_LOOPS)) == "publish"