from utils.validators import validate_email, validate_password, validate_upload, validate_resume_text
from utils.security import hash_password, verify_password, redact_pii


def test_email_and_password():
    assert validate_email("a@b.com")[0] and not validate_email("nope")[0]
    assert validate_password("Abcdef12")[0] and not validate_password("short")[0] and not validate_password("alllowercase1")[0]


def test_upload_validation():
    assert validate_upload("cv.pdf", b"%PDF-1.4 x")[0]
    assert not validate_upload("cv.pdf", b"not a pdf")[0]
    assert not validate_upload("cv.exe", b"MZ")[0]
    assert not validate_upload("cv.txt", b"")[0]
    assert not validate_upload("big.txt", b"a" * (6 * 1024 * 1024))[0]
    assert not validate_resume_text("too short")[0]


def test_password_hash_and_redaction():
    h = hash_password("Abcdef12"); assert h != "Abcdef12" and verify_password("Abcdef12", h) and not verify_password("x", h)
    out = redact_pii("mail me at a.b@x.com or +91 98765 43210 github.com/me")
    assert "@" not in out and "98765" not in out and "github" not in out
