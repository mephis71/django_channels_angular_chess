import pytest
from game.api.validators import is_fen_valid
from rest_framework.exceptions import ValidationError


@pytest.mark.parametrize(
    "fen",
    [
        "R7/1pk1NPP1/4pKB1/R4p2/4b3/2nP4/8/1Nb5 w - - 0 1",
        "8/2Rp1K2/1nb4B/p6P/p1kb4/1qP4p/p7/4r3 w - - 0 1",
        "1B3R2/1k3P2/8/P2r4/2P1BP2/1pRpQ1np/8/2K5 w - - 0 1",
    ],
)
def test_correct_fen_validator(fen):
    is_fen_valid(fen)


@pytest.mark.parametrize(
    "fen",
    [
        "R7/1pk1NPP1/4pKB1/R4p2/4b3/2asnP4/8/1Nb5 w - - 0 1",
        "8/2Rp1K2/1nb4B/p6P/p1k//b4/1qP4p/p7/4r3 w - - 0 1",
        "1B3R2/1k3P2/8/P//2r4/2P1BP2/1pRpQ1np/8/2K5 w - - 0 1",
    ],
)
def test_incorrect_fen_validator(fen):
    with pytest.raises(ValidationError, match="Fen is not valid."):
        is_fen_valid(fen)
