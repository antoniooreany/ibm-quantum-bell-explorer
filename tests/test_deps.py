import builtins
import pytest
from ibm_bell import deps

def test_install_idempotent(monkeypatch):
    # Simulate that packages are already importable
    monkeypatch.setattr(builtins, '__import__', lambda name, *a, **kw: None)
    # Ensure subprocess.check_call is not called
    called = {'value': False}
    def fake_check(*args, **kwargs):
        called['value'] = True
        raise AssertionError('pip should not be called')
    monkeypatch.setattr(deps.subprocess, 'check_call', fake_check)
    deps.install(['numpy'])
    assert not called['value']
