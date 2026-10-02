import pytest

from app.engine.safety import REDACTED, detect_hard_signals, redact


def codes(text: str) -> set[str]:
    return {rule.code for rule, _ in detect_hard_signals(text)}


@pytest.mark.parametrize(
    "text, expected",
    [
        ("He asked me to share the OTP I received", "OTP_REQUEST"),
        ("they said send the one-time password", "OTP_REQUEST"),
        ("To receive ₹5000 enter your UPI PIN", "UPI_PIN_REQUEST"),
        ("asked for my net banking login", "CREDENTIAL_REQUEST"),
        ("what is your CVV", "CREDENTIAL_REQUEST"),
        ("asked me for my demat login", "CREDENTIAL_REQUEST"),
        ("install AnyDesk so our team can help", "REMOTE_ACCESS_REQUEST"),
        ("please start screen sharing", "REMOTE_ACCESS_REQUEST"),
        ("give me your password", "PASSWORD_REQUEST"),
        ("அவர் ஓடிபி கேட்டார்", "OTP_REQUEST"),
        ("கடவுச்சொல் சொல்லுங்கள்", "PASSWORD_REQUEST"),
    ],
)
def test_hard_signals_detected(text, expected):
    assert expected in codes(text)


def test_one_time_password_is_otp_not_password():
    assert codes("send the one time password") == {"OTP_REQUEST"}


def test_benign_story_has_no_hard_signals():
    story = "My cousin told me about a mutual fund SIP through a SEBI registered distributor."
    assert codes(story) == set()


@pytest.mark.parametrize(
    "text, secret",
    [
        ("my OTP is 482913", "482913"),
        ("UPI PIN: 1234", "1234"),
        ("password is hunter2", "hunter2"),
        ("card 4111 1111 1111 1111 exp 12/28", "4111 1111 1111 1111"),
        ("ஓடிபி 556677", "556677"),
    ],
)
def test_redacts_credentials(text, secret):
    out, changed = redact(text)
    assert changed
    assert secret not in out
    assert REDACTED in out


def test_redaction_keeps_ordinary_numbers():
    text = "They asked for ₹25000 and called from 9876543210"
    assert redact(text) == (text, False)
