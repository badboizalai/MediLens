from medilens_worker.pipeline.state import DocStatus, next_status


def test_next_status() -> None:
    assert next_status(DocStatus.UPLOADED) == DocStatus.VALIDATED
    assert next_status(DocStatus.CONFIRMED) is None
